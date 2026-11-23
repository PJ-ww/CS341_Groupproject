-- Q2.2 ลักษณะประชากร (ขนาดหมู่บ้าน) และรายได้ครัวเรือน สัมพันธ์กับการถูกรายงานน้ำท่วมหรือไม่
-- แบ่งหมู่บ้านเป็น 4 กลุ่มเท่า ๆ กัน (quartile) แล้วเทียบสัดส่วนที่ถูกรายงานน้ำท่วม
-- รายได้: ใช้เฉพาะหมู่บ้านที่จับคู่รายได้ได้แบบ unique_match (ประมาณ 2 ใน 3 ของหมู่บ้าน)
WITH pop AS (
  SELECT 'population' AS dimension,
         NTILE(4) OVER (ORDER BY population_total) AS quartile,
         CAST(population_total AS DOUBLE) AS value, reports_total
  FROM flood_recovery_db.v_village_profile
  WHERE population_total IS NOT NULL
),
inc AS (
  SELECT 'avg_household_income' AS dimension,
         NTILE(4) OVER (ORDER BY avg_household_income) AS quartile,
         avg_household_income AS value, reports_total
  FROM flood_recovery_db.v_village_profile
  WHERE avg_household_income IS NOT NULL
),
both_dims AS (SELECT * FROM pop UNION ALL SELECT * FROM inc)
SELECT
  dimension,
  quartile,                                  -- 1 = ต่ำสุด, 4 = สูงสุด
  COUNT(*)              AS villages,
  ROUND(MIN(value), 0)  AS min_value,
  ROUND(MAX(value), 0)  AS max_value,
  ROUND(100.0 * SUM(CASE WHEN reports_total > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_flooded,
  ROUND(AVG(CAST(reports_total AS DOUBLE)), 2) AS avg_reports_per_village
FROM both_dims
GROUP BY dimension, quartile
ORDER BY dimension, quartile;