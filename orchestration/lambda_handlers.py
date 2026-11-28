"""Chiang Mai Flood Recovery - AWS Lambda handlers (Person 5).

Seven handlers share this one file. Each Lambda wraps the existing scripts from
ingestion/, transformation/scripts/ and storage/ WITHOUT changing them:
  1. copy the packaged scripts to /tmp/work (Lambda code dir is read-only)
  2. download the needed input files from S3 into the folders the scripts expect
  3. run the script with subprocess
  4. upload the outputs back to S3

The current pipeline handles five Chiang Mai source files for Buddhist years
2566-2567. Step Functions passes the same input to every step:
    {"bucket": "cs341-flood-recovery", "batch_id": "2026-11"}

Order: CheckBatch -> ValidateBatch -> (QuarantineBatch | TransformBatch) -> VerifyBatch
       -> CurateBatch (Parquet in curated/) -> QueryBatch (Glue tables + Athena dq/Q1-Q3).
QueryBatch is the last step, so it writes the _SUCCESS.json marker that CheckBatch looks for:
a batch that fails in any step can simply be run again with the same batch_id.
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

PKG_DIR = Path(__file__).resolve().parent          # /var/task in Lambda
WORK_DIR = Path(os.environ.get("WORK_DIR", "/tmp/work"))
DEFAULT_BUCKET = os.environ.get("BUCKET", "cs341-flood-recovery")
DATABASE = os.environ.get("ATHENA_DATABASE", "flood_recovery_db")
WORKGROUP = os.environ.get("ATHENA_WORKGROUP", "primary")
DDL_BUCKET = "cs341-flood-recovery"   # bucket written into sql/curated/01_create_curated_tables.sql

s3 = boto3.client("s3")

# order matters: integration runs after all four transformations
TRANSFORM_SCRIPTS = [
    "transform_flood.py",
    "transform_damage.py",
    "transform_household_income.py",
    "transform_village_mapping.py",
    "integrate_flood_mapping.py",
    "integrate_household_income_mapping.py",
]

# output file and expected rows from the committed transformation reports.
# Files are uploaded under transformation/output/ in S3.
DATASETS = [
    ("flood_2566_transformed.csv", 1198),
    ("flood_2567_transformed.csv", 3556),
    ("flood_chiangmai_combined.csv", 4754),
    ("chiangmai_damage_transformed.csv", 866),
    ("household_income_transformed.csv", 2154),
    ("village_mapping_transformed.csv", 2184),
    ("flood_mapping_integrated.csv", 4754),
    ("household_income_mapping_integrated.csv", 2154),
]
REPORTS = [
    "damage_transformation_report.json",
    "flood_mapping_integration_report.json",
    "flood_transformation_report.json",
    "household_income_mapping_integration_report.json",
    "household_income_transformation_report.json",
    "village_mapping_transformation_report.json",
]
TRANSFORMATION_PREFIX = "transformation/"
CURATED_PREFIX = "curated/"


# ---------------------------------------------------------------- helpers
def _params(event):
    bucket = event.get("bucket") or DEFAULT_BUCKET
    batch_id = event.get("batch_id")
    if not batch_id:
        raise ValueError("input must contain batch_id, e.g. {\"batch_id\": \"2026-11\"}")
    return bucket, str(batch_id)


def _marker_key(batch_id):
    return f"{TRANSFORMATION_PREFIX}_success/batch_id={batch_id}/_SUCCESS.json"


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
    if (PKG_DIR / "storage").exists():
        shutil.copytree(PKG_DIR / "storage", WORK_DIR / "storage")
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
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if isinstance(report, dict):
            quarantined = int(report.get("quarantined_count", 0))

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
    """Run Chiang Mai transformations and upload outputs/reports to S3."""
    bucket, batch_id = _params(event)
    wd = _prepare_workdir()

    # Download the five raw source files into the paths expected by config.py.
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix="raw/"):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith("/") or key.startswith("raw/_manifests/"):
                continue
            dest = wd / "ingestion" / "data" / key
            dest.parent.mkdir(parents=True, exist_ok=True)
            s3.download_file(bucket, key, str(dest))

    # Download validation outputs produced by ValidateBatch.
    cleaned_prefix = f"validation/batch_id={batch_id}/cleaned/"
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
    report_dir = wd / "transformation" / "reports"
    for fname, _ in DATASETS:
        source = out_dir / fname
        if not source.exists():
            raise RuntimeError(f"missing transformation output: {source}")
        s3.upload_file(str(source), bucket, f"{TRANSFORMATION_PREFIX}output/{fname}")
    for fname in REPORTS:
        source = report_dir / fname
        if not source.exists():
            raise RuntimeError(f"missing transformation report: {source}")
        s3.upload_file(str(source), bucket, f"{TRANSFORMATION_PREFIX}reports/{fname}")
    return {"datasets_uploaded": len(DATASETS), "reports_uploaded": len(REPORTS)}


# ---------------------------------------------------------------- 5. VerifyBatch
def verify_batch(event, context):
    """Verify every uploaded transformation CSV (row counts) and report."""
    bucket, batch_id = _params(event)
    counts, problems = {}, []
    local_dir = WORK_DIR / "verify"
    local_dir.mkdir(parents=True, exist_ok=True)
    for fname, expected in DATASETS:
        key = f"{TRANSFORMATION_PREFIX}output/{fname}"
        local_file = local_dir / fname
        try:
            s3.download_file(bucket, key, str(local_file))
        except ClientError as exc:
            problems.append(f"{key}: download failed ({exc})")
            continue
        with local_file.open(encoding="utf-8-sig", newline="") as stream:
            rows = sum(1 for _ in stream) - 1
        counts[fname] = rows
        if rows != expected:
            problems.append(f"{fname}: {rows} rows, expected {expected}")
    for fname in REPORTS:
        key = f"{TRANSFORMATION_PREFIX}reports/{fname}"
        try:
            s3.head_object(Bucket=bucket, Key=key)
        except ClientError as exc:
            problems.append(f"{key}: report missing ({exc})")

    if problems:
        raise RuntimeError("Verification failed: " + "; ".join(problems))
    return {"row_counts": counts}


# ---------------------------------------------------------------- 6. CurateBatch
def curate_batch(event, context):
    """Build the curated Parquet tables (storage/build_curated.py) and upload them to curated/."""
    bucket, batch_id = _params(event)
    wd = _prepare_workdir()

    out_dir = wd / "transformation" / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    for fname, _ in DATASETS:
        s3.download_file(bucket, f"{TRANSFORMATION_PREFIX}output/{fname}", str(out_dir / fname))

    proc = _run(wd / "storage" / "build_curated.py", wd)
    if proc.returncode != 0:
        raise RuntimeError(f"build_curated.py failed: {(proc.stdout + proc.stderr)[-800:]}")
    report_path = wd / "storage" / "reports" / "curated_build_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    # same behaviour as storage/upload_to_s3.py: clear each table prefix first,
    # because Athena reads every file under a table LOCATION
    curated_dir = wd / "storage" / "curated"
    uploaded = 0
    for table in report["tables"]:
        prefix = f"{CURATED_PREFIX}{table}/"
        stale = []
        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
            stale += [{"Key": o["Key"]} for o in page.get("Contents", [])]
        for i in range(0, len(stale), 1000):
            s3.delete_objects(Bucket=bucket, Delete={"Objects": stale[i:i + 1000]})
        for f in sorted((curated_dir / table).rglob("*.parquet")):
            s3.upload_file(str(f), bucket, prefix + f.relative_to(curated_dir / table).as_posix())
            uploaded += 1
    s3.upload_file(str(report_path), bucket, f"storage/reports/batch_id={batch_id}/curated_build_report.json")

    table_rows = {t: info["output_rows"] for t, info in report["tables"].items()}
    return {"table_rows": table_rows, "parquet_files": uploaded}


# ---------------------------------------------------------------- 7. QueryBatch
def _sql_files():
    sql_dir = PKG_DIR / "sql" / "curated"
    setup = [sql_dir / "01_create_curated_tables.sql", sql_dir / "02_create_views.sql"]
    checks = sorted((sql_dir / "data_quality").glob("*.sql")) + sorted((sql_dir / "queries").glob("*.sql"))
    return setup, checks


def _quality_problems(results, table_rows):
    """dq_01 rows per table must equal what CurateBatch wrote; dq_02 keys must be unique and not null."""
    problems = []
    rows = results.get("dq_01_row_counts") or []
    if len(rows) < 2:
        return ["dq_01_row_counts returned no rows"]
    athena_rows = {}
    for r in rows[1:]:
        rec = dict(zip(rows[0], r))
        athena_rows[rec["table_name"]] = athena_rows.get(rec["table_name"], 0) + int(float(rec["row_count"]))
    for table, expected in table_rows.items():
        if athena_rows.get(table) != expected:
            problems.append(f"{table}: Athena sees {athena_rows.get(table)} rows, curated has {expected}")
    rows = results.get("dq_02_primary_keys") or []
    for r in rows[1:]:
        rec = dict(zip(rows[0], r))
        if float(rec["duplicate_keys"] or 0) != 0 or float(rec["null_keys"] or 0) != 0:
            problems.append(f"{rec['table_name']}: duplicate_keys={rec['duplicate_keys']}, "
                            f"null_keys={rec['null_keys']}")
    return problems


def query_batch(event, context):
    """Register the curated tables/views in the Glue Data Catalog through Athena DDL, run the
    data quality checks and the Q1-Q3 queries, save every result to S3, then write the
    success marker (only after everything passed)."""
    import csv
    import io

    bucket, batch_id = _params(event)
    sys.path.insert(0, str(PKG_DIR / "storage"))
    import run_athena  # storage/run_athena.py: statements(), run(), fetch()

    athena = boto3.client("athena")
    output = f"s3://{bucket}/athena-results/"
    setup, checks = _sql_files()

    for f in setup:
        for stmt in run_athena.statements(f):
            run_athena.run(athena, stmt.replace(f"s3://{DDL_BUCKET}/", f"s3://{bucket}/"), output, WORKGROUP)
        print(f"ok  {f.name}")

    results, scanned_total = {}, 0
    for f in checks:
        qid = None
        for stmt in run_athena.statements(f):
            qid, scanned = run_athena.run(athena, stmt, output, WORKGROUP)
            scanned_total += scanned
        rows = run_athena.fetch(athena, qid)
        results[f.stem] = rows
        buf = io.StringIO()
        csv.writer(buf).writerows(rows)
        s3.put_object(Bucket=bucket, Key=f"query_results/batch_id={batch_id}/{f.stem}.csv",
                      ContentType="text/csv", Body=buf.getvalue().encode("utf-8-sig"))
        print(f"ok  {f.name:45s} rows={len(rows) - 1}")

    table_rows = (event.get("curate") or {}).get("table_rows") or {}
    problems = _quality_problems(results, table_rows)
    if problems:
        raise RuntimeError("Data quality failed: " + "; ".join(problems))

    marker = {"batch_id": batch_id, "status": "SUCCESS",
              "transformation_row_counts": (event.get("verify") or {}).get("row_counts"),
              "curated_table_rows": table_rows,
              "queries": sorted(results),
              "athena_scanned_bytes": scanned_total,
              "time": datetime.now(timezone.utc).isoformat()}
    s3.put_object(Bucket=bucket, Key=_marker_key(batch_id), ContentType="application/json",
                  Body=json.dumps(marker, indent=2).encode("utf-8"))
    return {"queries_saved": len(results), "athena_scanned_bytes": scanned_total}
