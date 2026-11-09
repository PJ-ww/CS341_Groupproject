-- CS341 Flood Impact & Recovery
-- Analytical SQL queries used in Amazon Athena
-- Database: flood_recovery_db
-- หมายเหตุ: ใช้ชื่อคอลัมน์ตาม Glue Data Catalog และครอบชื่อภาษาไทยด้วย double quotes

-- =========================================================
-- 01. Geographic: การกระจายระดับความเสี่ยง
-- =========================================================
SELECT
    "ความเสี่ยง" AS risk_level,
    COUNT(*) AS total_records,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM geographic
GROUP BY "ความเสี่ยง"
ORDER BY total_records DESC;


-- =========================================================
-- 02. Geographic: จำนวนพื้นที่ความเสี่ยงสูงและสูงมากแยกตามอำเภอ
-- =========================================================
SELECT
    "อำเภอ" AS district,
    COUNT(*) AS total_areas,
    SUM(CASE WHEN "ความเสี่ยง" = 'เสี่ยงสูง' THEN 1 ELSE 0 END) AS high_risk,
    SUM(CASE WHEN "ความเสี่ยง" = 'เสี่ยงสูงมาก' THEN 1 ELSE 0 END) AS very_high_risk,
    SUM(CASE
        WHEN "ความเสี่ยง" IN ('เสี่ยงสูง', 'เสี่ยงสูงมาก') THEN 1
        ELSE 0
    END) AS total_high_and_very_high,
    ROUND(
        SUM(CASE
            WHEN "ความเสี่ยง" IN ('เสี่ยงสูง', 'เสี่ยงสูงมาก') THEN 1
            ELSE 0
        END) * 100.0 / COUNT(*),
        2
    ) AS high_risk_percentage
FROM geographic
GROUP BY "อำเภอ"
ORDER BY total_high_and_very_high DESC;


-- =========================================================
-- 03. Geographic: การกระจายความเสี่ยงแยกตามปี
-- =========================================================
SELECT
    "ปี" AS year,
    "ความเสี่ยง" AS risk_level,
    COUNT(*) AS total_records
FROM geographic
GROUP BY "ปี", "ความเสี่ยง"
ORDER BY year, risk_level;


-- =========================================================
-- 04. NSO Income: ค่าเฉลี่ยรายได้ตามกลุ่มเศรษฐกิจและปี
-- =========================================================
SELECT
    year,
    soc_eco_class1,
    COUNT(*) AS total_records,
    ROUND(AVG(value), 2) AS average_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value
FROM nso_income
GROUP BY year, soc_eco_class1
ORDER BY year, average_value DESC;


-- =========================================================
-- 05. NSO Income: ค่าเฉลี่ยตามจังหวัดในปี 2568
-- =========================================================
SELECT
    province,
    COUNT(*) AS total_records,
    ROUND(AVG(value), 2) AS average_value
FROM nso_income
WHERE year = 2568
GROUP BY province
ORDER BY average_value DESC;


-- =========================================================
-- 06. Disaster Budget: งบประมาณแยกตามจังหวัด ปี 2564
-- =========================================================
SELECT
    "จังหวัด" AS province,
    COUNT(*) AS total_records,
    ROUND(SUM("วงเงิน"), 2) AS total_budget,
    ROUND(SUM("วงเงินอนุมัติ"), 2) AS total_approved,
    ROUND(SUM("รวมทั้งสิ้น"), 2) AS total_reported
FROM disaster_budget
WHERE "ปี" = 2564
GROUP BY "จังหวัด"
ORDER BY total_approved DESC NULLS LAST;