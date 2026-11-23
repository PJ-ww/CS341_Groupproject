"""Build the curated zone: typed, partitioned Parquet tables (Person 4).

Input : transformation/output/*.csv  (Person 3)
Output: storage/curated/<table>/[source_year=YYYY/]part-0.parquet
        storage/reports/curated_build_report.json

Rules
- Every column gets the type declared in storage/schema.py. A value that does
  not convert (e.g. text in a number column) stops the build instead of being
  silently turned into NULL.
- Administrative codes are stored as strings with a fixed length
  (village_code = 8 digits) so leading zeros and '.0' float artefacts from CSV
  cannot break joins.
- No rows are dropped or invented: output rows must equal input rows.
- The build is idempotent: each table folder is deleted and rewritten.

Run:  python storage/build_curated.py
"""

import json
import shutil
import sys
from datetime import datetime, timezone

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from schema import CURATED_DIR, REPORT_DIR, ROOT, TABLES, village_columns  # noqa: E402

ARROW = {"string": pa.string(), "int": pa.int32(), "bigint": pa.int64(),
         "double": pa.float64(), "date": pa.date32()}


class BuildError(Exception):
    pass


def norm_code(series, length, col):
    """'50200301', '50200301.0' -> '50200301'; check digits and length."""
    s = series.str.strip().str.replace(r"\.0+$", "", regex=True)
    bad = s.notna() & ~s.str.fullmatch(r"\d+", na=False)
    if bad.any():
        raise BuildError(f"{col}: non-numeric codes {s[bad].unique()[:5].tolist()}")
    s = s.where(s.isna(), s.str.zfill(length))
    wrong = s.notna() & (s.str.len() != length)
    if wrong.any():
        raise BuildError(f"{col}: expected {length} digits, got {s[wrong].unique()[:5].tolist()}")
    return s


def cast(series, typ, col):
    s = series.where(series.isna(), series.str.strip()).replace("", pd.NA)
    if typ == "string":
        return s
    if typ == "date":
        out = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")
        bad = s.notna() & out.isna()
        if bad.any():
            raise BuildError(f"{col}: bad dates {s[bad].unique()[:5].tolist()}")
        return out.dt.date
    out = pd.to_numeric(s, errors="coerce")
    bad = s.notna() & out.isna()
    if bad.any():
        raise BuildError(f"{col}: not a number {s[bad].unique()[:5].tolist()}")
    if typ in ("int", "bigint"):
        frac = out.notna() & (out % 1 != 0)
        if frac.any():
            raise BuildError(f"{col}: non-integer values {out[frac].unique()[:5].tolist()}")
        return out.astype("Int64")
    return out.astype("float64")


def read_source(path):
    return pd.read_csv(path, dtype=str, keep_default_na=True, encoding="utf-8-sig")


def district_lookup():
    m = read_source(TABLES["dim_village"]["source"])
    pairs = m[["district_name", "district_code"]].drop_duplicates()
    if pairs["district_name"].duplicated().any():
        raise BuildError("district_name maps to more than one district_code")
    return dict(zip(pairs["district_name"], norm_code(pairs["district_code"], 4, "district_code")))


def prepare(name, spec, raw):
    """Return (dataframe in declared column order, column spec)."""
    df = raw.copy()
    notes = []

    if name == "dim_village":
        cols = village_columns(df.columns)
        # mapping stores subdistrict as 8 digits ending in '00' (50010100);
        # flood data uses 6 digits (500101). Standardise on 6 digits.
        sd = df["subdistrict_code"].str.replace(r"\.0+$", "", regex=True)
        if not sd.str.endswith("00").all():
            raise BuildError("dim_village.subdistrict_code: not all end with '00'")
        df["subdistrict_code"] = sd.str[:6]
        notes.append("subdistrict_code แปลงจาก 8 หลัก (xxxxxx00) เป็น 6 หลักให้ตรงกับข้อมูลน้ำท่วม")

    elif name == "fact_disaster_damage":
        cols = spec["columns"]
        lookup = district_lookup()
        df["district_code"] = df["district"].str.strip().map(lookup)
        miss = df["district_code"].isna()
        if miss.any():
            raise BuildError(f"damage districts not in dim_village: {df.loc[miss, 'district'].unique().tolist()}")
        notes.append("เพิ่ม district_code โดยเทียบชื่ออำเภอกับ dim_village (ตรงกันครบทุกแถว)")

    elif name == "fact_household_income":
        cols = spec["columns"]
        for c, expect in (("statistic", "รายได้ครัวเรือนเฉลี่ย"), ("unit", "บาท/ปี")):
            vals = df[c].dropna().unique().tolist()
            if vals != [expect]:
                raise BuildError(f"income.{c} expected only '{expect}', got {vals}")
        notes.append("ตัดคอลัมน์ statistic/unit ที่มีค่าเดียวทั้งตาราง แล้วใส่หน่วยไว้ในชื่อคอลัมน์แทน")
        df = df.rename(columns={"income": "avg_household_income_baht_per_year"})
        df["income_record_id"] = [f"inc-{i:06d}" for i in range(1, len(df) + 1)]
        lookup = district_lookup()
        df["district_code"] = df["district"].str.strip().map(lookup)
        # attributes from mapping are kept only in dim_village (no duplication)
        not_unique = df["mapping_match_status"] != "unique_match"
        if df.loc[not_unique, "village_code"].notna().any():
            raise BuildError("income: village_code present on a non unique_match row")
        notes.append("เก็บเฉพาะ village_code + mapping_match_status; คุณลักษณะหมู่บ้านดึงจาก dim_village ตอน query")

    else:
        cols = spec["columns"]

    part = spec["partition"]
    out = pd.DataFrame(index=df.index)
    for col, typ in cols:
        if col not in df.columns:
            raise BuildError(f"{name}: source has no column '{col}'")
        if col in spec["code_lengths"]:
            out[col] = norm_code(df[col], spec["code_lengths"][col], col)
        else:
            out[col] = cast(df[col], typ, col)
    if part:
        out[part[0]] = cast(df[part[0]], part[1], part[0])
    return out, cols, notes


def write_table(name, spec, df, cols):
    target = CURATED_DIR / name
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    fields = [pa.field(c, ARROW[t]) for c, t in cols]
    part = spec["partition"]
    if part:
        fields.append(pa.field(part[0], ARROW[part[1]]))
    table = pa.Table.from_pandas(df, schema=pa.schema(fields), preserve_index=False)

    if part:
        ds.write_dataset(
            table, target, format="parquet",
            partitioning=ds.partitioning(pa.schema([fields[-1]]), flavor="hive"),
            basename_template="part-{i}.parquet",
            existing_data_behavior="delete_matching",
            file_options=ds.ParquetFileFormat().make_write_options(compression="snappy"),
        )
    else:
        pq.write_table(table, target / "part-0.parquet", compression="snappy")
    return table


def check_pk(df, keys):
    dup = df.duplicated(subset=keys).sum()
    nulls = int(df[keys].isna().any(axis=1).sum())
    return int(dup), nulls


def main():
    report = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "output_dir": "storage/curated", "tables": {}, "checks": []}
    failed = False

    for name, spec in TABLES.items():
        raw = read_source(spec["source"])
        df, cols, notes = prepare(name, spec, raw)
        write_table(name, spec, df, cols)

        files = sorted((CURATED_DIR / name).rglob("*.parquet"))
        written_rows = sum(pq.ParquetFile(f).metadata.num_rows for f in files)
        dup, pk_nulls = check_pk(df, spec["primary_key"])
        part = spec["partition"]
        partitions = ({str(k): int(v) for k, v in df[part[0]].value_counts().sort_index().items()}
                      if part else None)

        info = {
            "source_file": spec["source"].relative_to(ROOT).as_posix(),
            "grain": spec["grain"],
            "primary_key": spec["primary_key"],
            "partition_column": part[0] if part else None,
            "partitions": partitions,
            "source_rows": len(raw),
            "output_rows": written_rows,
            "columns": len(cols) + (1 if part else 0),
            "parquet_files": [f.relative_to(ROOT).as_posix() for f in files],
            "csv_bytes": spec["source"].stat().st_size,
            "parquet_bytes": sum(f.stat().st_size for f in files),
            "notes": notes,
        }
        report["tables"][name] = info

        for check, ok in (
            (f"{name}: output rows == source rows ({written_rows} vs {len(raw)})", written_rows == len(raw)),
            (f"{name}: primary key {spec['primary_key']} unique (duplicates={dup})", dup == 0),
            (f"{name}: primary key not null (null rows={pk_nulls})", pk_nulls == 0),
        ):
            report["checks"].append({"check": check, "passed": bool(ok)})
            failed |= not ok
        print(f"{name:24s} rows={written_rows:>5}  files={len(files)}  "
              f"csv={info['csv_bytes']/1024:7.1f}KB -> parquet={info['parquet_bytes']/1024:6.1f}KB")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / "curated_build_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"report -> {out.relative_to(ROOT)}")
    if failed:
        print("SOME CHECKS FAILED:", [c["check"] for c in report["checks"] if not c["passed"]])
        sys.exit(1)
    print("all checks passed")


if __name__ == "__main__":
    try:
        main()
    except BuildError as e:
        print("BUILD FAILED:", e)
        sys.exit(1)
