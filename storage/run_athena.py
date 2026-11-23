"""Run curated SQL files on Amazon Athena and save the results (Person 4).

Examples
  python storage/run_athena.py --sql sql/curated/01_create_curated_tables.sql
  python storage/run_athena.py --sql sql/curated/02_create_views.sql
  python storage/run_athena.py --sql sql/curated/data_quality --sql sql/curated/queries --save

--save writes the last statement's result of each file to
storage/athena_results/<file>.csv so the numbers can be compared with the
local DuckDB run in storage/query_results/.
Needs AWS credentials with Athena, Glue and S3 access.
"""

import argparse
import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from schema import BUCKET, DATABASE, ROOT  # noqa: E402


def statements(path):
    text = "\n".join(l for l in path.read_text(encoding="utf-8").splitlines()
                     if not l.strip().startswith("--"))
    return [s.strip() for s in text.split(";") if s.strip()]


def run(athena, sql, output, workgroup):
    kwargs = {"QueryString": sql, "ResultConfiguration": {"OutputLocation": output},
              "WorkGroup": workgroup}
    if not sql.upper().startswith("CREATE DATABASE"):
        kwargs["QueryExecutionContext"] = {"Database": DATABASE}
    qid = athena.start_query_execution(**kwargs)["QueryExecutionId"]
    while True:
        st = athena.get_query_execution(QueryExecutionId=qid)["QueryExecution"]
        state = st["Status"]["State"]
        if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(1)
    if state != "SUCCEEDED":
        raise RuntimeError(f"{state}: {st['Status'].get('StateChangeReason')}\n{sql[:300]}")
    scanned = st.get("Statistics", {}).get("DataScannedInBytes", 0)
    return qid, scanned


def fetch(athena, qid):
    rows = []
    for page in athena.get_paginator("get_query_results").paginate(QueryExecutionId=qid):
        for r in page["ResultSet"]["Rows"]:
            rows.append([c.get("VarCharValue", "") for c in r["Data"]])
    return rows  # first row is the header


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sql", action="append", required=True, help="SQL file or folder (repeatable)")
    ap.add_argument("--bucket", default=BUCKET)
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--workgroup", default="primary")
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    import boto3
    athena = boto3.client("athena", region_name=args.region)
    output = f"s3://{args.bucket}/athena-results/"
    out_dir = ROOT / "storage" / "athena_results"

    files = []
    for p in map(Path, args.sql):
        files += sorted(p.glob("*.sql")) if p.is_dir() else [p]

    for f in files:
        qid = None
        for stmt in statements(f):
            qid, scanned = run(athena, stmt, output, args.workgroup)
        print(f"ok  {f.name:45s} last query {qid}  scanned={scanned / 1024:.1f} KB")
        if args.save and qid:
            out_dir.mkdir(parents=True, exist_ok=True)
            with open(out_dir / f"{f.stem}.csv", "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(fetch(athena, qid))


if __name__ == "__main__":
    main()
