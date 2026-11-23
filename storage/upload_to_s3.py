"""Upload the curated Parquet tables to S3 (Person 4).

storage/curated/<table>/...  ->  s3://<bucket>/curated/<table>/...
Each table prefix is cleared first so a rerun leaves no stale files
(Athena reads every file under LOCATION).

Run:  python storage/upload_to_s3.py --dry-run     # show what would happen
      python storage/upload_to_s3.py               # needs AWS credentials
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from schema import BUCKET, CURATED_DIR, ROOT, S3_PREFIX, TABLES  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", default=BUCKET)
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    s3 = None
    if not args.dry_run:
        import boto3
        s3 = boto3.client("s3", region_name=args.region)

    for name in TABLES:
        local = CURATED_DIR / name
        files = sorted(local.rglob("*.parquet"))
        if not files:
            sys.exit(f"{local.relative_to(ROOT)} is empty; run storage/build_curated.py first")
        prefix = f"{S3_PREFIX}{name}/"

        if s3:
            stale = []
            for page in s3.get_paginator("list_objects_v2").paginate(Bucket=args.bucket, Prefix=prefix):
                stale += [{"Key": o["Key"]} for o in page.get("Contents", [])]
            for i in range(0, len(stale), 1000):
                s3.delete_objects(Bucket=args.bucket, Delete={"Objects": stale[i:i + 1000]})
            if stale:
                print(f"deleted {len(stale)} old object(s) under s3://{args.bucket}/{prefix}")

        for f in files:
            key = prefix + f.relative_to(local).as_posix()
            print(f"{'[dry-run] ' if args.dry_run else ''}{f.relative_to(ROOT)} -> s3://{args.bucket}/{key}")
            if s3:
                s3.upload_file(str(f), args.bucket, key)


if __name__ == "__main__":
    main()
