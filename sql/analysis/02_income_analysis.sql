-- CS341 Flood Impact & Recovery
-- NSO Income Analysis
-- Database: flood_recovery_db

-- 05. ค่าเฉลี่ยรายได้ตามกลุ่มเศรษฐกิจและปี
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


-- 06. ค่าเฉลี่ยตามจังหวัดในปี 2568
SELECT
    province,
    COUNT(*) AS total_records,
    ROUND(AVG(value), 2) AS average_value
FROM nso_income
WHERE year = 2568
GROUP BY province
ORDER BY average_value DESC;


-- 07. ค่าเฉลี่ยรายได้แยกตามกลุ่มเศรษฐกิจของจังหวัดยโสธร
SELECT
    year,
    soc_eco_class1,
    COUNT(*) AS total_records,
    ROUND(AVG(value), 2) AS average_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value
FROM nso_income
WHERE province = 'ยโสธร'
  AND year IN (2566, 2568)
GROUP BY year, soc_eco_class1
ORDER BY year, average_value DESC;