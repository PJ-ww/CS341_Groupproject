"""CS341 Flood Recovery - AWS Lambda handlers (Person 5).

Five handlers share this one file. Each Lambda wraps the existing scripts from
ingestion/ and transformation/scripts/ WITHOUT changing them:
  1. copy the packaged scripts to /tmp/work (Lambda code dir is read-only)
  2. download the needed input files from S3 into the folders the scripts expect
  3. run the script with subprocess
  4. upload the outputs back to S3

Step Functions passes the same input to every step:
    {"bucket": "cs341-flood-recovery", "batch_id": "2026-11"}
"""
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

PKG_DIR = Path(__file__).resolve().parent          # /var/task in Lambda
WORK_DIR = Path(os.environ.get("WORK_DIR", "/tmp/work"))
DEFAULT_BUCKET = os.environ.get("BUCKET", "cs341-flood-recovery")
DATABASE = os.environ.get("ATHENA_DATABASE", "flood_recovery_db")
ATHENA_OUTPUT_PREFIX = "athena-results/"

s3 = boto3.client("s3")
athena = boto3.client("athena")

# order matters: integrate_data needs create_features + transform_nso_income first
TRANSFORM_SCRIPTS = [
    "clean_data.py", "standardize.py", "create_features.py",
    "transform_flood_village_stats.py", "transform_nso_income.py",
    "transform_disaster_budget.py", "transform_flood_affected_households.py",
    "transform_affected_households_summary.py", "integrate_data.py",
]

# athena table / processed folder, output file, expected rows (Person 3 + 4 reports)
DATASETS = [
    ("geographic", "geographic_data_features.csv", 1772),
    ("flood_village_stats", "flood_village_stats_transformed.parquet", 57024),
    ("nso_income", "nso_household_income_transformed.parquet", 15400),
    ("disaster_budget", "disaster_budget_2564_transformed.parquet", 76),
    ("flood_affected_households", "flood_affected_households_transformed.parquet", 144),
    ("affected_households_summary", "affected_households_summary_transformed.parquet", 48),
    ("geographic_nso_integrated", "geographic_nso_integrated.parquet", 10),
]


# ---------------------------------------------------------------- helpers
def _params(event):
    bucket = event.get("bucket") or DEFAULT_BUCKET
    batch_id = event.get("batch_id")
    if not batch_id:
        raise ValueError("input must contain batch_id, e.g. {\"batch_id\": \"2026-11\"}")
    return bucket, str(batch_id)


def _marker_key(batch_id):
    return f"processed/_success/batch_id={batch_id}/_SUCCESS.json"


def _key_exists(bucket, key):
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as exc:
        if exc.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
            return False
        raise


def _load_config():
    sys.path.insert(0, str(PKG_DIR / "ingestion"))
    import config  # ingestion/config.py (FILES: local_file -> s3 prefix/name)
    return config


def _prepare_workdir():
    """Fresh copy of ingestion/ and transformation/scripts in /tmp (scripts write next to themselves)."""
    shutil.rmtree(WORK_DIR, ignore_errors=True)
    (WORK_DIR / "ingestion").mkdir(parents=True)
    (WORK_DIR / "transformation").mkdir(parents=True)
    shutil.copytree(PKG_DIR / "ingestion", WORK_DIR / "ingestion", dirs_exist_ok=True)
    shutil.copytree(PKG_DIR / "transformation" / "scripts", WORK_DIR / "transformation" / "scripts")
    return WORK_DIR


def _run(script, cwd):
    print(f"RUN {script.relative_to(WORK_DIR)}")
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(p for p in sys.path if p)}
    proc = subprocess.run([sys.executable, str(script)], cwd=cwd, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=env)
    print(proc.stdout[-3000:])
    if proc.stderr:
        print("STDERR:", proc.stderr[-3000:])
    return proc


def _upload_tree(local_dir, bucket, prefix):
    count = 0
    for path in Path(local_dir).rglob("*"):
        if path.is_file():
            key = prefix + path.relative_to(local_dir).as_posix()
            s3.upload_file(str(path), bucket, key)
            count += 1
    return count


# ---------------------------------------------------------------- 1. CheckBatch
def check_batch(event, context):
    """Has this batch already been processed? (looks for the _SUCCESS.json marker)"""
    bucket, batch_id = _params(event)
    done = _key_exists(bucket, _marker_key(batch_id))
    print(f"batch {batch_id} already processed: {done}")
    return {"already_processed": done}


# ---------------------------------------------------------------- 2. ValidateBatch
def validate_batch(event, context):
    """Run ingestion/validate_data.py on the raw files. valid = no file failed to read."""
    bucket, batch_id = _params(event)
    cfg = _load_config()
    wd = _prepare_workdir()
    data_dir = wd / "ingestion" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    missing = []
    for item in cfg.FILES:
        key = item["s3_prefix"] + item["s3_name"]
        try:
            s3.download_file(bucket, key, str(data_dir / item["local_file"]))
        except ClientError:
            missing.append(key)
    if missing:
        return {"valid": False, "quarantined_rows": 0,
                "reason": "missing files in S3: " + ", ".join(missing)}

    proc = _run(wd / "ingestion" / "validate_data.py", wd / "ingestion")
    valid = proc.returncode == 0

    report_path = wd / "validation" / "reports" / "validation_report.json"
    quarantined = 0
    if report_path.exists():
        for rep in json.loads(report_path.read_text(encoding="utf-8")):
            for table in rep.get("sheets", {"csv": rep}).values():
                quarantined += table.get("quarantined_count", 0) if isinstance(table, dict) else 0

    _upload_tree(wd / "validation", bucket, f"validation/batch_id={batch_id}/")
    reason = "ok" if valid else "validate_data.py failed: " + (proc.stdout + proc.stderr)[-500:]
    return {"valid": valid, "quarantined_rows": quarantined, "reason": reason}


# ---------------------------------------------------------------- 3. QuarantineBatch
def quarantine_batch(event, context):
    """Invalid batch: copy the source files to quarantine/ together with the reason."""
    bucket, batch_id = _params(event)
    cfg = _load_config()
    prefix = f"quarantine/batch_id={batch_id}/"
    copied = 0
    for item in cfg.FILES:
        key = item["s3_prefix"] + item["s3_name"]
        try:
            s3.copy_object(Bucket=bucket, Key=prefix + item["s3_name"],
                           CopySource={"Bucket": bucket, "Key": key})
            copied += 1
        except ClientError:
            pass
    s3.put_object(Bucket=bucket, Key=prefix + "reason.json", ContentType="application/json",
                  Body=json.dumps({"batch_id": batch_id, "validation": event.get("validation"),
                                   "time": datetime.now(timezone.utc).isoformat()},
                                  ensure_ascii=False, indent=2).encode("utf-8"))
    return {"quarantined_files": copied}


# ---------------------------------------------------------------- 4. TransformBatch
def transform_batch(event, context):
    """Run the 9 transformation scripts of Person 3, upload the 7 datasets to processed/."""
    bucket, batch_id = _params(event)
    cfg = _load_config()
    wd = _prepare_workdir()

    # raw/<prefix>/<s3_name> -> ingestion/data/<local_file>  (same layout the scripts expect)
    data_dir = wd / "ingestion" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    for item in cfg.FILES:
        s3.download_file(bucket, item["s3_prefix"] + item["s3_name"], str(data_dir / item["local_file"]))

    # validation/cleaned -> validation/cleaned  (clean_data.py reads the deduplicated geographic file)
    cleaned_prefix = f"validation/batch_id={batch_id}/cleaned/"
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=cleaned_prefix):
        for obj in page.get("Contents", []):
            dest = wd / "validation" / "cleaned" / obj["Key"][len(cleaned_prefix):]
            dest.parent.mkdir(parents=True, exist_ok=True)
            s3.download_file(bucket, obj["Key"], str(dest))

    for name in TRANSFORM_SCRIPTS:
        proc = _run(wd / "transformation" / "scripts" / name, wd)
        if proc.returncode != 0:
            raise RuntimeError(f"{name} failed: {(proc.stderr or proc.stdout)[-800:]}")

    out_dir = wd / "transformation" / "output"
    for folder, fname, _ in DATASETS:
        s3.upload_file(str(out_dir / fname), bucket, f"processed/{folder}/{fname}")
    _upload_tree(wd / "transformation" / "reports", bucket, f"reports/batch_id={batch_id}/")
    return {"datasets_uploaded": len(DATASETS)}


# ---------------------------------------------------------------- 5. VerifyBatch
def verify_batch(event, context):
    """Count rows of every table with Athena, compare with the expected numbers, write _SUCCESS.json."""
    bucket, batch_id = _params(event)
    output = f"s3://{bucket}/{ATHENA_OUTPUT_PREFIX}"

    ids = {}
    for table, _, _ in DATASETS:
        ids[table] = athena.start_query_execution(
            QueryString=f"SELECT COUNT(*) AS n FROM {table}",
            QueryExecutionContext={"Database": DATABASE},
            ResultConfiguration={"OutputLocation": output})["QueryExecutionId"]

    counts, problems = {}, []
    for table, _, expected in DATASETS:
        qid = ids[table]
        for _ in range(60):                       # wait up to ~2 minutes
            state = athena.get_query_execution(QueryExecutionId=qid)["QueryExecution"]["Status"]
            if state["State"] in ("SUCCEEDED", "FAILED", "CANCELLED"):
                break
            time.sleep(2)
        if state["State"] != "SUCCEEDED":
            problems.append(f"{table}: query {state['State']} {state.get('StateChangeReason', '')}")
            continue
        rows = athena.get_query_results(QueryExecutionId=qid)["ResultSet"]["Rows"]
        counts[table] = int(rows[1]["Data"][0]["VarCharValue"])
        if counts[table] != expected:
            problems.append(f"{table}: {counts[table]} rows, expected {expected}")

    if problems:
        raise RuntimeError("Verification failed: " + "; ".join(problems))

    marker = {"batch_id": batch_id, "status": "SUCCESS", "row_counts": counts,
              "time": datetime.now(timezone.utc).isoformat()}
    s3.put_object(Bucket=bucket, Key=_marker_key(batch_id), ContentType="application/json",
                  Body=json.dumps(marker, indent=2).encode("utf-8"))
    return marker