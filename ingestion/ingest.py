import hashlib, json, logging, os
from datetime import datetime, timezone

import boto3
import requests

from config import BUCKET, REGION, SOURCES

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
s3 = boto3.client("s3", region_name=REGION)


def download(url, local_path):
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    with open(local_path, "wb") as f:
        f.write(r.content)
    return len(r.content)


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def already_uploaded(key, checksum):
    """ข้ามถ้าไฟล์เดิมเหมือนกัน -> รันซ้ำได้ (idempotent)"""
    try:
        head = s3.head_object(Bucket=BUCKET, Key=key)
        return head["Metadata"].get("md5") == checksum
    except s3.exceptions.ClientError:
        return False


def main():
    os.makedirs("data", exist_ok=True)
    manifest = []
    for src in SOURCES:
        local = os.path.join("data", src["filename"])
        key = src["s3_prefix"] + src["filename"]
        try:
            logging.info("Downloading %s", src["name"])
            size = download(src["url"], local)
            checksum = md5(local)

            if already_uploaded(key, checksum):
                logging.info("Skip (unchanged): %s", key)
                status = "skipped"
            else:
                s3.upload_file(
                    local, BUCKET, key,
                    ExtraArgs={"Metadata": {"md5": checksum, "source_url": src["url"][:1000]}},
                )
                logging.info("Uploaded s3://%s/%s", BUCKET, key)
                status = "uploaded"

            manifest.append({"source": src["name"], "s3_key": key, "bytes": size,
                             "md5": checksum, "status": status,
                             "ingested_at": datetime.now(timezone.utc).isoformat()})
        except Exception as e:
            logging.error("FAILED %s: %s", src["name"], e)
            manifest.append({"source": src["name"], "status": "failed", "error": str(e)})

    # เก็บ manifest ไว้เป็นหลักฐาน (data lineage)
    mkey = f"raw/_manifests/manifest_{datetime.now(timezone.utc):%Y%m%dT%H%M%S}.json"
    s3.put_object(Bucket=BUCKET, Key=mkey, Body=json.dumps(manifest, ensure_ascii=False, indent=2))
    logging.info("Manifest written: %s", mkey)


if __name__ == "__main__":
    main()