import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from config import BUCKET, FILES, REGION

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
s3 = boto3.client("s3", region_name=REGION)
DATA_DIR = Path(__file__).parent / "data"


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def already_uploaded(key, checksum):
    """ไฟล์เดิมเหมือนกัน -> ข้าม ทำให้รันซ้ำได้ (idempotent)"""
    try:
        head = s3.head_object(Bucket=BUCKET, Key=key)
        return head["Metadata"].get("md5") == checksum
    except ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
            return False
        raise


def main():
    manifest = []
    for item in FILES:
        local = DATA_DIR / item["local_file"]
        key = item["s3_prefix"] + item["s3_name"]
        entry = {"local_file": item["local_file"], "s3_key": key, "source": item["source"]}
        try:
            if not local.exists():
                raise FileNotFoundError(local)
            checksum = md5(local)
            entry.update(bytes=local.stat().st_size, md5=checksum)

            if already_uploaded(key, checksum):
                entry["status"] = "skipped"
                logging.info("Skip (unchanged): %s", key)
            else:
                s3.upload_file(
                    str(local), BUCKET, key,
                    ExtraArgs={"Metadata": {"md5": checksum}},
                )
                entry["status"] = "uploaded"
                logging.info("Uploaded s3://%s/%s", BUCKET, key)
        except Exception as e:
            entry.update(status="failed", error=str(e))
            logging.error("FAILED %s: %s", item["local_file"], e)

        entry["source_url"] = item["source_url"]
        entry["ingested_at"] = datetime.now(timezone.utc).isoformat()
        manifest.append(entry)

    mkey = f"raw/_manifests/manifest_{datetime.now(timezone.utc):%Y%m%dT%H%M%S}.json"
    s3.put_object(
        Bucket=BUCKET, Key=mkey,
        Body=json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"),
    )
    logging.info("Manifest written: s3://%s/%s", BUCKET, mkey)

    failed = [m for m in manifest if m["status"] == "failed"]
    if failed:
        raise SystemExit(f"{len(failed)} file(s) failed")


if __name__ == "__main__":
    main()