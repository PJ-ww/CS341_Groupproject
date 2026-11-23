# Storage, Data Model & Query (คนที่ 4)

แปลงผลลัพธ์จาก `transformation/output/` เป็นตาราง Parquet แบบมีชนิดข้อมูลและ partition แล้วลงทะเบียนใน Glue Data Catalog เพื่อ Query ด้วย Amazon Athena
เหตุผลการออกแบบดูที่ [`docs/06-storage-data-model-query.md`](../docs/06-storage-data-model-query.md)

## ไฟล์

| ไฟล์ | หน้าที่ |
|---|---|
| `schema.py` | นิยามตาราง (grain, primary key, partition, ชนิดข้อมูลทุกคอลัมน์) ไว้ที่เดียว |
| `build_curated.py` | CSV → Parquet ใน `storage/curated/` พร้อมตรวจจำนวนแถวและ PK แล้วเขียน `reports/curated_build_report.json` |
| `generate_ddl.py` | สร้าง `sql/curated/01_create_curated_tables.sql` จาก `schema.py` |
| `run_local_queries.py` | ทดสอบ SQL ทั้งหมดบนเครื่องด้วย DuckDB (ไม่ต้องใช้ AWS) แล้วบันทึกผลที่ `query_results/` |
| `upload_to_s3.py` | อัปโหลด `storage/curated/` ไปที่ `s3://cs341-flood-recovery/curated/` |
| `run_athena.py` | รันไฟล์ SQL บน Athena และบันทึกผลที่ `athena_results/` |

```text
sql/curated/
├── 01_create_curated_tables.sql   # DDL (auto-generated) + partition projection
├── 02_create_views.sql            # v_flood_report_village, v_village_profile
├── 03_iceberg_optional.sql        # ตัวอย่าง Iceberg + time travel (ไม่บังคับ)
├── data_quality/dq_01..dq_04      # row count, PK, join coverage, completeness
└── queries/q1_* q2_* q3_*         # ตอบคำถามวิจัย Q1–Q3
```

## วิธีรัน

### A. บนเครื่อง (ไม่ต้องใช้ AWS)

```bash
python -m pip install -r requirements.txt      # มี duckdb แล้ว
python storage/build_curated.py                 # → storage/curated/*.parquet
python storage/run_local_queries.py             # → storage/query_results/*.csv + README.md
```

### B. บน AWS (Athena)

```bash
python storage/upload_to_s3.py --dry-run        # ตรวจ path ก่อน
python storage/upload_to_s3.py
python storage/run_athena.py --sql sql/curated/01_create_curated_tables.sql
python storage/run_athena.py --sql sql/curated/02_create_views.sql
python storage/run_athena.py --sql sql/curated/data_quality --sql sql/curated/queries --save
```

หรือเปิด Athena Query Editor แล้วรันทีละ statement จากไฟล์เดียวกัน (database: `flood_recovery_db`)
ผลใน `storage/athena_results/` ต้องตรงกับ `storage/query_results/` ซึ่งใช้เป็นหลักฐานว่า query บน cloud ให้ผลเท่ากับที่ทดสอบในเครื่อง

## S3 Layout

```text
s3://cs341-flood-recovery/
├── transformation/ ...                         # คนที่ 3
└── curated/                                    # คนที่ 4
    ├── dim_village/part-0.parquet
    ├── fact_flood_report/source_year=2566/part-0.parquet
    ├── fact_flood_report/source_year=2567/part-0.parquet
    ├── fact_disaster_damage/source_year=2563..2567/part-0.parquet
    └── fact_household_income/part-0.parquet
```
