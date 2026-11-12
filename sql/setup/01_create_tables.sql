-- CS341 Flood Impact & Recovery
-- Athena DDL: สร้าง database และ 7 ตารางที่ sql/analysis/*, sql/data_quality/* และ VerifyBatch (orchestration/lambda_handlers.py) ใช้
--
-- วิธีใช้: เปิด Athena console (region us-east-1) ตั้ง Query result location เป็น s3://<BUCKET>/athena-results/
-- แล้วรันทีละ statement (Athena รันได้ครั้งละ 1 statement)
-- ถ้าใช้ bucket อื่นที่ไม่ใช่ cs341-flood-recovery ให้แทนที่ชื่อ bucket ใน LOCATION ทุกตาราง
--
-- ก่อนรัน ต้องมีไฟล์อยู่ใน S3 ตามตำแหน่งนี้แล้ว (TransformBatch อัปโหลดให้ หรืออัปโหลดเองตาม orchestration/README.md ขั้นที่ 2):
--   processed/geographic/geographic_data_features.csv
--   processed/flood_village_stats/flood_village_stats_transformed.parquet
--   processed/nso_income/nso_household_income_transformed.parquet
--   processed/disaster_budget/disaster_budget_2564_transformed.parquet
--   processed/flood_affected_households/flood_affected_households_transformed.parquet
--   processed/affected_households_summary/affected_households_summary_transformed.parquet
--   processed/geographic_nso_integrated/geographic_nso_integrated.parquet
--
-- ชนิดคอลัมน์ได้จาก schema ของไฟล์ใน transformation/output/ (int64 -> BIGINT, double -> DOUBLE, string -> STRING)
-- จำนวนแถวที่ควรได้ (ตรงกับ DATASETS ใน lambda_handlers.py) อยู่ท้ายไฟล์


CREATE DATABASE IF NOT EXISTS flood_recovery_db;


-- 1. geographic (CSV, 1,772 แถว)
CREATE EXTERNAL TABLE IF NOT EXISTS flood_recovery_db.geographic (
    `ปี`              INT,
    `รายการ`          STRING,
    `อำเภอ`           STRING,
    `ตำบล`            STRING,
    `หมู่ที่`           STRING,
    `ความเสี่ยง`       STRING,
    `เหล่งที่มา`        STRING,
    `risk_level_code` INT,
    `risk_level`      STRING
)
ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 's3://cs341-flood-recovery/processed/geographic/'
TBLPROPERTIES ('skip.header.line.count' = '1');


-- 2. flood_village_stats (Parquet, 57,024 แถว)
CREATE EXTERNAL TABLE IF NOT EXISTS flood_recovery_db.flood_village_stats (
    `province_code`             STRING,
    `province_name`             STRING,
    `amphur_code`               STRING,
    `amphur_name`               STRING,
    `district_code`             STRING,
    `district_name`             STRING,
    `moo_no`                    STRING,
    `org_code`                  STRING,
    `org_name`                  STRING,
    `community_name`            STRING,
    `moo_id`                    STRING,
    `dis_type_name`             STRING,
    `y2562`                     BIGINT,
    `y2563`                     BIGINT,
    `y2564`                     BIGINT,
    `y2565`                     BIGINT,
    `y2566`                     BIGINT,
    `y2567`                     BIGINT,
    `years_with_reported_value` BIGINT
)
STORED AS PARQUET
LOCATION 's3://cs341-flood-recovery/processed/flood_village_stats/';


-- 3. nso_income (Parquet, 15,400 แถว)
CREATE EXTERNAL TABLE IF NOT EXISTS flood_recovery_db.nso_income (
    `year`           BIGINT,
    `province`       STRING,
    `source_income1` STRING,
    `source_income2` STRING,
    `source_income3` STRING,
    `soc_eco_class1` STRING,
    `soc_eco_class2` STRING,
    `value`          DOUBLE,
    `unit`           STRING,
    `attribute`      STRING,
    `source`         STRING
)
STORED AS PARQUET
LOCATION 's3://cs341-flood-recovery/processed/nso_income/';


-- 4. disaster_budget (Parquet, 76 แถว)
CREATE EXTERNAL TABLE IF NOT EXISTS flood_recovery_db.disaster_budget (
    `ปี`                   BIGINT,
    `ที่`                   BIGINT,
    `จังหวัด`               STRING,
    `ด้านดำรงชีพ`           DOUBLE,
    `ด้านสังคมสงเคราะห์`     DOUBLE,
    `ด้านการแพทย์`          DOUBLE,
    `ด้านเกษตรพืช`          DOUBLE,
    `ด้านเกษตรประมง`        DOUBLE,
    `ด้านเกษตรปศุสัตว์`       DOUBLE,
    `ด้านเกษตรอื่น`          DOUBLE,
    `ด้านบรรเทา`            DOUBLE,
    `ด้านการปฏิบัติงานให้`    DOUBLE,
    `ป้องกันหรือยับยั้ง`       DOUBLE,
    `รวมทั้งสิ้น`             DOUBLE,
    `วงเงิน`                DOUBLE,
    `วงเงินอนุมัติ`           DOUBLE,
    `วงเงินไม่อนุมัติ`         DOUBLE
)
STORED AS PARQUET
LOCATION 's3://cs341-flood-recovery/processed/disaster_budget/';


-- 5. flood_affected_households (Parquet, 144 แถว)
CREATE EXTERNAL TABLE IF NOT EXISTS flood_recovery_db.flood_affected_households (
    `ปี`      BIGINT,
    `รายการ`  STRING,
    `อำเภอ`   STRING,
    `ตำบล`    STRING,
    `จำนวน`   BIGINT,
    `หน่วย`   STRING,
    `ที่มา`    STRING
)
STORED AS PARQUET
LOCATION 's3://cs341-flood-recovery/processed/flood_affected_households/';


-- 6. affected_households_summary (Parquet, 48 แถว)
CREATE EXTERNAL TABLE IF NOT EXISTS flood_recovery_db.affected_households_summary (
    `ครั้งที่`    STRING,
    `อำเภอ`    STRING,
    `รายการ`   STRING,
    `จำนวน`    BIGINT,
    `หน่วยนับ`  STRING
)
STORED AS PARQUET
LOCATION 's3://cs341-flood-recovery/processed/affected_households_summary/';


-- 7. geographic_nso_integrated (Parquet, 10 แถว)
CREATE EXTERNAL TABLE IF NOT EXISTS flood_recovery_db.geographic_nso_integrated (
    `จังหวัด`                  STRING,
    `ปี`                      BIGINT,
    `income_indicator`        STRING,
    `socioeconomic_group`     STRING,
    `monthly_income_value`    DOUBLE,
    `income_unit`             STRING,
    `geographic_area_records` BIGINT,
    `risk_very_low_count`     BIGINT,
    `risk_low_count`          BIGINT,
    `risk_moderate_count`     BIGINT,
    `risk_high_count`         BIGINT,
    `risk_very_high_count`    BIGINT,
    `risk_very_low_pct`       DOUBLE,
    `risk_low_pct`            DOUBLE,
    `risk_moderate_pct`       DOUBLE,
    `risk_high_pct`           DOUBLE,
    `risk_very_high_pct`      DOUBLE
)
STORED AS PARQUET
LOCATION 's3://cs341-flood-recovery/processed/geographic_nso_integrated/';


-- (ไม่บังคับ) ตาราง partition ตามปีของ NSO ตามที่อธิบายใน docs/data-model.md
-- CREATE TABLE flood_recovery_db.nso_income_partitioned
-- WITH (format = 'PARQUET',
--       external_location = 's3://cs341-flood-recovery/processed/nso_income_partitioned/',
--       partitioned_by = ARRAY['year'])
-- AS SELECT province, source_income1, source_income2, source_income3, soc_eco_class1, soc_eco_class2,
--           value, unit, attribute, source, year
--    FROM flood_recovery_db.nso_income;


-- ตรวจผล: จำนวนแถวต้องเท่ากับ 1772 / 57024 / 15400 / 76 / 144 / 48 / 10
SELECT 'geographic' AS table_name, COUNT(*) AS n FROM flood_recovery_db.geographic
UNION ALL SELECT 'flood_village_stats', COUNT(*) FROM flood_recovery_db.flood_village_stats
UNION ALL SELECT 'nso_income', COUNT(*) FROM flood_recovery_db.nso_income
UNION ALL SELECT 'disaster_budget', COUNT(*) FROM flood_recovery_db.disaster_budget
UNION ALL SELECT 'flood_affected_households', COUNT(*) FROM flood_recovery_db.flood_affected_households
UNION ALL SELECT 'affected_households_summary', COUNT(*) FROM flood_recovery_db.affected_households_summary
UNION ALL SELECT 'geographic_nso_integrated', COUNT(*) FROM flood_recovery_db.geographic_nso_integrated;
