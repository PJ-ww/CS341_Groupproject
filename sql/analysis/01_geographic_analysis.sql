-- CS341 Flood Impact & Recovery
-- Geographic Risk Analysis
-- Database: flood_recovery_db

-- 01. การกระจายระดับความเสี่ยงทั้งหมด
SELECT
    "ความเสี่ยง" AS risk_level,
    COUNT(*) AS total_records,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM geographic
GROUP BY "ความเสี่ยง"
ORDER BY total_records DESC;


-- 02. จำนวนพื้นที่ความเสี่ยงสูงและสูงมากแยกตามอำเภอ
SELECT
    "อำเภอ" AS district,
    COUNT(*) AS total_areas,
    SUM(CASE WHEN "ความเสี่ยง" = 'เสี่ยงสูง' THEN 1 ELSE 0 END) AS high_risk,
    SUM(CASE WHEN "ความเสี่ยง" = 'เสี่ยงสูงมาก' THEN 1 ELSE 0 END) AS very_high_risk,
    SUM(CASE
        WHEN "ความเสี่ยง" IN ('เสี่ยงสูง', 'เสี่ยงสูงมาก')
        THEN 1 ELSE 0
    END) AS high_and_very_high,
    ROUND(
        100.0 * SUM(CASE
            WHEN "ความเสี่ยง" IN ('เสี่ยงสูง', 'เสี่ยงสูงมาก')
            THEN 1 ELSE 0
        END) / COUNT(*), 2
    ) AS high_risk_pct
FROM geographic
GROUP BY "อำเภอ"
ORDER BY high_and_very_high DESC;


-- 03. การกระจายความเสี่ยงแยกตามปี
SELECT
    "ปี" AS year,
    "ความเสี่ยง" AS risk_level,
    COUNT(*) AS total_records
FROM geographic
GROUP BY "ปี", "ความเสี่ยง"
ORDER BY year, risk_level;


-- 04. เปรียบเทียบความเสี่ยงของพื้นที่เดียวกันระหว่างปี 2567 และ 2568
WITH a AS (
    SELECT
        "อำเภอ" AS amphur,
        "ตำบล" AS tambon,
        "หมู่ที่" AS moo,
        "ความเสี่ยง" AS risk
    FROM geographic
    WHERE "ปี" = 2567
),
b AS (
    SELECT
        "อำเภอ" AS amphur,
        "ตำบล" AS tambon,
        "หมู่ที่" AS moo,
        "ความเสี่ยง" AS risk
    FROM geographic
    WHERE "ปี" = 2568
),
joined AS (
    SELECT
        a.amphur,
        a.tambon,
        a.moo,
        a.risk AS risk_2567,
        b.risk AS risk_2568
    FROM a
    FULL OUTER JOIN b
        ON a.amphur = b.amphur
        AND a.tambon = b.tambon
        AND a.moo IS NOT DISTINCT FROM b.moo
)
SELECT
    COUNT(*) AS total_area_keys,
    COUNT(risk_2567) AS areas_2567,
    COUNT(risk_2568) AS areas_2568,
    SUM(CASE WHEN risk_2567 = risk_2568 THEN 1 ELSE 0 END) AS same_risk,
    SUM(CASE
        WHEN risk_2567 IS NOT NULL
         AND risk_2568 IS NOT NULL
         AND risk_2567 <> risk_2568
        THEN 1 ELSE 0
    END) AS changed_risk,
    SUM(CASE
        WHEN risk_2567 IS NULL OR risk_2568 IS NULL
        THEN 1 ELSE 0
    END) AS missing_year
FROM joined;