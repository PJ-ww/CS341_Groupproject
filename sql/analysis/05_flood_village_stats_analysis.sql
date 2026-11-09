-- CS341 Flood Impact & Recovery
-- Flood Village Statistics Analysis
-- Database: flood_recovery_db

-- 17. ความครอบคลุมของข้อมูลรายปีแยกตามจังหวัด
SELECT
    province_name,
    COUNT(*) AS total_records,
    COUNT(y2562) AS reported_2562,
    COUNT(y2563) AS reported_2563,
    COUNT(y2564) AS reported_2564,
    COUNT(y2565) AS reported_2565,
    COUNT(y2566) AS reported_2566,
    COUNT(y2567) AS reported_2567
FROM flood_village_stats
GROUP BY province_name
ORDER BY total_records DESC;


-- 18. ข้อมูลอุทกภัยของจังหวัดยโสธรแยกตามปี
SELECT
    province_name,
    dis_type_name,
    COUNT(*) AS total_records,
    COUNT(y2562) AS reported_2562,
    COUNT(y2563) AS reported_2563,
    COUNT(y2564) AS reported_2564,
    COUNT(y2565) AS reported_2565,
    COUNT(y2566) AS reported_2566,
    COUNT(y2567) AS reported_2567
FROM flood_village_stats
WHERE province_name = 'ยโสธร'
  AND dis_type_name = 'อุทกภัย'
GROUP BY province_name, dis_type_name;


-- 19. ผลรวมและค่าเฉลี่ยของค่ารายปีในจังหวัดยโสธร
SELECT
    province_name,
    dis_type_name,
    SUM(y2562) AS total_2562,
    SUM(y2563) AS total_2563,
    SUM(y2564) AS total_2564,
    SUM(y2565) AS total_2565,
    SUM(y2566) AS total_2566,
    SUM(y2567) AS total_2567,
    AVG(y2562) AS avg_2562,
    AVG(y2563) AS avg_2563,
    AVG(y2564) AS avg_2564,
    AVG(y2565) AS avg_2565,
    AVG(y2566) AS avg_2566,
    AVG(y2567) AS avg_2567
FROM flood_village_stats
WHERE province_name = 'ยโสธร'
  AND dis_type_name = 'อุทกภัย'
GROUP BY province_name, dis_type_name;


-- 20. การกระจายค่าที่รายงานเป็น 1 และ 2 แยกตามปีในจังหวัดยโสธร
SELECT
    '2562' AS year,
    COUNT(y2562) AS reported_records,
    SUM(CASE WHEN y2562 = 1 THEN 1 ELSE 0 END) AS value_1_records,
    SUM(CASE WHEN y2562 = 2 THEN 1 ELSE 0 END) AS value_2_records,
    MIN(y2562) AS min_value,
    MAX(y2562) AS max_value
FROM flood_village_stats
WHERE province_name = 'ยโสธร'
  AND dis_type_name = 'อุทกภัย'

UNION ALL

SELECT
    '2564',
    COUNT(y2564),
    SUM(CASE WHEN y2564 = 1 THEN 1 ELSE 0 END),
    SUM(CASE WHEN y2564 = 2 THEN 1 ELSE 0 END),
    MIN(y2564),
    MAX(y2564)
FROM flood_village_stats
WHERE province_name = 'ยโสธร'
  AND dis_type_name = 'อุทกภัย'

UNION ALL

SELECT
    '2565',
    COUNT(y2565),
    SUM(CASE WHEN y2565 = 1 THEN 1 ELSE 0 END),
    SUM(CASE WHEN y2565 = 2 THEN 1 ELSE 0 END),
    MIN(y2565),
    MAX(y2565)
FROM flood_village_stats
WHERE province_name = 'ยโสธร'
  AND dis_type_name = 'อุทกภัย'

UNION ALL

SELECT
    '2566',
    COUNT(y2566),
    SUM(CASE WHEN y2566 = 1 THEN 1 ELSE 0 END),
    SUM(CASE WHEN y2566 = 2 THEN 1 ELSE 0 END),
    MIN(y2566),
    MAX(y2566)
FROM flood_village_stats
WHERE province_name = 'ยโสธร'
  AND dis_type_name = 'อุทกภัย';


-- 21. การกระจายค่า 1 และ 2 แยกตามอำเภอ ปี 2564 และ 2566
SELECT
    amphur_name,
    COUNT(y2564) AS reported_2564,
    SUM(CASE WHEN y2564 = 1 THEN 1 ELSE 0 END) AS value_1_2564,
    SUM(CASE WHEN y2564 = 2 THEN 1 ELSE 0 END) AS value_2_2564,
    ROUND(
        100.0 * SUM(CASE WHEN y2564 = 2 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(y2564), 0), 2
    ) AS value_2_pct_2564,
    COUNT(y2566) AS reported_2566,
    SUM(CASE WHEN y2566 = 1 THEN 1 ELSE 0 END) AS value_1_2566,
    SUM(CASE WHEN y2566 = 2 THEN 1 ELSE 0 END) AS value_2_2566,
    ROUND(
        100.0 * SUM(CASE WHEN y2566 = 2 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(y2566), 0), 2
    ) AS value_2_pct_2566
FROM flood_village_stats
WHERE province_name = 'ยโสธร'
  AND dis_type_name = 'อุทกภัย'
GROUP BY amphur_name
ORDER BY reported_2564 DESC, reported_2566 DESC;


-- 22. รายละเอียดหมู่บ้านที่มีค่าเท่ากับ 2 ในปี 2564 หรือ 2566
SELECT
    province_name,
    amphur_name,
    district_name,
    moo_no,
    community_name,
    y2564,
    y2566
FROM flood_village_stats
WHERE province_name = 'ยโสธร'
  AND dis_type_name = 'อุทกภัย'
  AND (y2564 = 2 OR y2566 = 2)
ORDER BY amphur_name, district_name, moo_no;


-- 23. เปรียบเทียบการเปลี่ยนค่าระหว่างปี 2564 และ 2566
SELECT
    y2564 AS value_2564,
    y2566 AS value_2566,
    COUNT(*) AS record_count
FROM flood_village_stats
WHERE province_name = 'ยโสธร'
  AND dis_type_name = 'อุทกภัย'
  AND y2564 IS NOT NULL
  AND y2566 IS NOT NULL
GROUP BY y2564, y2566
ORDER BY y2564, y2566;


-- 24. ตรวจสอบ years_with_reported_value
WITH checked AS (
    SELECT
        years_with_reported_value,
        (
            CASE WHEN y2562 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN y2563 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN y2564 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN y2565 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN y2566 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN y2567 IS NOT NULL THEN 1 ELSE 0 END
        ) AS calculated_years
    FROM flood_village_stats
)
SELECT
    COUNT(*) AS total_records,
    SUM(CASE
        WHEN years_with_reported_value = calculated_years
        THEN 1 ELSE 0
    END) AS matching_records,
    SUM(CASE
        WHEN years_with_reported_value <> calculated_years
        THEN 1 ELSE 0
    END) AS mismatching_records
FROM checked;


-- 25. การกระจายจำนวนปีที่แต่ละ record มีข้อมูล
SELECT
    years_with_reported_value,
    COUNT(*) AS total_records,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2
    ) AS percentage
FROM flood_village_stats
GROUP BY years_with_reported_value
ORDER BY years_with_reported_value;