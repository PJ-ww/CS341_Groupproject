import hashlib
import json
import logging
import mimetypes
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from config import BUCKET, FILES, REGION

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
s3 = boto3.client("s3", region_name=REGION)
DATA_DIR = Path(__file__).parent / "data"


def md5(path):
    """คำนวณ MD5 ของไฟล์เพื่อใช้ตรวจว่าไฟล์เปลี่ยนหรือไม่"""
    digest = hashlib.md5()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def already_uploaded(key, checksum):
    """ถ้าไฟล์ใน S3 มี MD5 ตรงกัน ให้ข้ามเพื่อให้รันซ้ำได้"""
    try:
        head = s3.head_object(Bucket=BUCKET, Key=key)
        return head.get("Metadata", {}).get("md5") == checksum
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code in ("404", "NoSuchKey", "NotFound"):
            return False
        raise


def main():
    manifest = []

    for item in FILES:
        local = DATA_DIR / item["local_file"]
        key = item["s3_prefix"] + item["s3_name"]
        entry = {
            "local_file": item["local_file"],
            "s3_key": key,
            "source": item.get("source", ""),
            "source_url": item.get("source_url", ""),
        }

        try:
            if not local.is_file():
                raise FileNotFoundError(f"ไม่พบไฟล์หรือไม่ใช่ไฟล์ปกติ: {local}")

            checksum = md5(local)
            entry.update(bytes=local.stat().st_size, md5=checksum)

            if already_uploaded(key, checksum):
                entry["status"] = "skipped"
                logging.info("Skip (unchanged): s3://%s/%s", BUCKET, key)
            else:
                content_type, _ = mimetypes.guess_type(local.name)
                extra_args = {"Metadata": {"md5": checksum}}
                if content_type:
                    extra_args["ContentType"] = content_type

                s3.upload_file(str(local), BUCKET, key, ExtraArgs=extra_args)
                entry["status"] = "uploaded"
                logging.info("Uploaded s3://%s/%s", BUCKET, key)

        except Exception as exc:
            entry.update(status="failed", error=str(exc))
            logging.error("FAILED %s: %s", item["local_file"], exc)

        entry["ingested_at"] = datetime.now(timezone.utc).isoformat()
        manifest.append(entry)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    manifest_key = f"raw/_manifests/manifest_{timestamp}.json"

    s3.put_object(
        Bucket=BUCKET,
        Key=manifest_key,
        Body=json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"),
        ContentType="application/json; charset=utf-8",
    )
    logging.info("Manifest written: s3://%s/%s", BUCKET, manifest_key)

    failed = [item for item in manifest if item["status"] == "failed"]
    if failed:
        raise SystemExit(f"{len(failed)} file(s) failed; ตรวจสอบ log และ manifest")


if __name__ == "__main__":
    main()
