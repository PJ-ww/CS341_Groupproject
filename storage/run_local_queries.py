"""Test the curated tables and SQL locally with DuckDB (no AWS needed).

It registers each Parquet table under the same name Athena uses
(flood_recovery_db.<table>), creates the views from sql/curated/02_create_views.sql,
then runs every file in sql/curated/data_quality/ and sql/curated/queries/
unchanged. Results go to storage/query_results/<query>.csv and a summary
markdown file that can be pasted into the report.

Run:  python storage/build_curated.py && python storage/run_local_queries.py
"""

import sys
from pathlib import Path

import duckdb
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from schema import CURATED_DIR, DATABASE, ROOT, TABLES  # noqa: E402

SQL_DIR = ROOT / "sql" / "curated"
OUT_DIR = ROOT / "storage" / "query_results"


def statements(path):
    text = "\n".join(l for l in path.read_text(encoding="utf-8").splitlines()
                     if not l.strip().startswith("--"))
    return [s.strip() for s in text.split(";") if s.strip()]


def to_markdown(df, max_rows=30):
    df = df.head(max_rows)
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in row) + " |")
    return "\n".join(lines)


def main():
    con = duckdb.connect()
    con.execute(f"CREATE SCHEMA {DATABASE}")
    for name, spec in TABLES.items():
        glob = (CURATED_DIR / name / ("*/*.parquet" if spec["partition"] else "*.parquet")).as_posix()
        hive = "true" if spec["partition"] else "false"
        con.execute(f"CREATE VIEW {DATABASE}.{name} AS "
                    f"SELECT * FROM read_parquet('{glob}', hive_partitioning={hive})")
    for stmt in statements(SQL_DIR / "02_create_views.sql"):
        con.execute(stmt)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = ["# Query results (local DuckDB run on curated Parquet)", "",
               "สร้างโดย `python storage/run_local_queries.py` — ใช้ไฟล์ SQL ชุดเดียวกับที่รันบน Athena", ""]
    failed = []
    files = sorted((SQL_DIR / "data_quality").glob("*.sql")) + sorted((SQL_DIR / "queries").glob("*.sql"))
    for f in files:
        try:
            df = con.execute(statements(f)[-1]).df()
        except Exception as e:  # keep going, report at the end
            failed.append(f"{f.name}: {e}")
            print(f"FAIL {f.name}: {e}")
            continue
        df.to_csv(OUT_DIR / f"{f.stem}.csv", index=False, encoding="utf-8-sig")
        title = next((l[3:] for l in f.read_text(encoding="utf-8").splitlines() if l.startswith("-- ")), f.stem)
        summary += [f"## {f.stem}", "", f"_{title}_", "", to_markdown(df), ""]
        print(f"ok   {f.name:45s} rows={len(df)}")

    (OUT_DIR / "README.md").write_text("\n".join(summary), encoding="utf-8")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
