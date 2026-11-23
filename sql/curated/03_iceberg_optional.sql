-- OPTIONAL: Apache Iceberg version of fact_flood_report (Athena engine v3).
-- ไม่ได้ใช้เป็นตารางหลัก (ตารางหลักคือ Parquet + Hive partition ใน 01_create_curated_tables.sql)
-- ใช้สาธิตว่าถ้าต้องการ "เก็บประวัติแต่ละ batch" (ปัญหา processed/ ถูกเขียนทับใน Issue #15)
-- Iceberg ทำได้ด้วย snapshot + time travel โดยไม่ต้องคัดลอกไฟล์เอง
-- Trade-off: มี metadata/manifest เพิ่ม, ต้องใช้ Athena v3, และข้อมูลเรามีแค่ ~5k แถวต่อรอบ

DROP TABLE IF EXISTS flood_recovery_db.fact_flood_report_iceberg;

CREATE TABLE flood_recovery_db.fact_flood_report_iceberg
WITH (
  table_type   = 'ICEBERG',
  is_external  = false,
  location     = 's3://cs341-flood-recovery/curated_iceberg/fact_flood_report/',
  format       = 'PARQUET',
  partitioning = ARRAY['source_year']
) AS
SELECT * FROM flood_recovery_db.fact_flood_report;

-- ดู snapshot ทั้งหมด (1 snapshot ต่อการเขียน 1 ครั้ง)
SELECT committed_at, snapshot_id, operation
FROM "flood_recovery_db"."fact_flood_report_iceberg$snapshots"
ORDER BY committed_at;

-- ตัวอย่าง time travel (แทน timestamp ด้วยเวลาจริงจากผลลัพธ์ด้านบน)
-- SELECT source_year, COUNT(*) FROM flood_recovery_db.fact_flood_report_iceberg
-- FOR TIMESTAMP AS OF TIMESTAMP '2026-11-25 10:00:00 UTC'
-- GROUP BY source_year;
