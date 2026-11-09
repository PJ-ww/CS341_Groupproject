-- CS341 Flood Impact & Recovery
-- Affected Households Analysis
-- Database: flood_recovery_db

-- 10. จำนวนครัวเรือนรวมแยกตามปี
SELECT
    "ปี" AS year,
    COUNT(*) AS total_records,
    SUM("จำนวน") AS total_reported,
    MIN("จำนวน") AS min_reported,
    MAX("จำนวน") AS max_reported
FROM flood_affected_households
GROUP BY "ปี"
ORDER BY year;


-- 11. จำนวนครัวเรือนแยกตามอำเภอและปี
SELECT
    "ปี" AS year,
    "อำเภอ" AS amphur,
    COUNT(*) AS total_records,
    SUM("จำนวน") AS total_reported,
    MAX("จำนวน") AS max_reported
FROM flood_affected_households
GROUP BY "ปี", "อำเภอ"
ORDER BY year, total_reported DESC;


-- 12. จำนวน records และจำนวนอำเภอ แยกตามหน่วยนับ
SELECT
    "หน่วยนับ" AS unit,
    COUNT(*) AS total_records,
    COUNT(DISTINCT "อำเภอ") AS district_count
FROM affected_households_summary
GROUP BY "หน่วยนับ"
ORDER BY unit;


-- 13. จำนวนครัวเรือนในแต่ละอำเภอและรอบรายงาน
SELECT
    "ครั้งที่" AS report_round,
    "อำเภอ" AS amphur,
    "จำนวน" AS reported_households
FROM affected_households_summary
WHERE "หน่วยนับ" = 'ครัวเรือน'
ORDER BY "อำเภอ", TRY_CAST("ครั้งที่" AS INTEGER);


-- 14. ค่าสูงสุดและต่ำสุดที่รายงานในแต่ละอำเภอ แยกตามหน่วย
SELECT
    "อำเภอ" AS amphur,
    "หน่วยนับ" AS unit,
    COUNT(*) AS report_records,
    MIN("จำนวน") AS min_reported,
    MAX("จำนวน") AS max_reported
FROM affected_households_summary
GROUP BY "อำเภอ", "หน่วยนับ"
ORDER BY unit, max_reported DESC;


-- 15. จำนวนตำบลและหมู่บ้านสูงสุดที่รายงานในแต่ละอำเภอ
SELECT
    "อำเภอ" AS amphur,
    MAX(CASE WHEN "หน่วยนับ" = 'ตำบล'
        THEN "จำนวน" END) AS max_subdistricts,
    MAX(CASE WHEN "หน่วยนับ" = 'หมู่บ้าน'
        THEN "จำนวน" END) AS max_villages
FROM affected_households_summary
GROUP BY "อำเภอ"
ORDER BY max_subdistricts DESC;


-- 16. ตรวจสอบอำเภอ/หน่วยที่มีหลายรอบรายงาน
SELECT
    "อำเภอ" AS amphur,
    "รายการ" AS item,
    "หน่วยนับ" AS unit,
    COUNT(*) AS report_records,
    COUNT(DISTINCT "ครั้งที่") AS report_rounds
FROM affected_households_summary
GROUP BY "อำเภอ", "รายการ", "หน่วยนับ"
HAVING COUNT(*) > 1
ORDER BY report_records DESC, amphur;