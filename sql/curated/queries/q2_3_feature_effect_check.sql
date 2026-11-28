-- Q2.3 ตรวจว่าความต่างใน q2_1 / q2_2 มากกว่าความบังเอิญหรือไม่ และยังอยู่ไหมเมื่อเทียบภายในอำเภอเดียวกัน
-- outcome = หมู่บ้านถูกรายงานน้ำท่วมอย่างน้อย 1 ครั้ง (2566-2567)
-- z = two-proportion z-test (|z| > 1.96 ประมาณ p < 0.05) สมมติว่าหมู่บ้านเป็นอิสระต่อกัน ซึ่งไม่จริงทั้งหมด (หมู่บ้านใกล้กันน้ำท่วมพร้อมกัน)
-- within_district_diff_pp = ค่าเฉลี่ยถ่วงน้ำหนักของความต่างในแต่ละอำเภอ (น้ำหนัก n1*n0/(n1+n0) แบบ Mantel-Haenszel)
--   ใช้ตัดผลของ "อยู่อำเภอไหน" ออก เช่น หมู่บ้านภูเขากระจุกอยู่ในอำเภอที่ถูกรายงานบ่อย
-- low_income = รายได้อยู่ครึ่งล่าง (NTILE 2) เฉพาะหมู่บ้านที่จับคู่รายได้ได้
WITH v AS (
  SELECT district_code, village_code,
         CASE WHEN reports_total > 0 THEN 1 ELSE 0 END AS flooded,
         COALESCE(river_flag, 0) AS river_flag,
         COALESCE(mountain_flag, 0) AS mountain_flag,
         avg_household_income
  FROM flood_recovery_db.v_village_profile
),
income_half AS (
  SELECT district_code, flooded,
         CASE WHEN NTILE(2) OVER (ORDER BY avg_household_income, village_code) = 1 THEN 1 ELSE 0 END AS flag
  FROM v
  WHERE avg_household_income IS NOT NULL
),
base AS (
  SELECT 'river (แม่น้ำ/ลำน้ำ)' AS feature, district_code, river_flag AS flag, flooded FROM v
  UNION ALL
  SELECT 'mountain (ภูเขา)', district_code, mountain_flag, flooded FROM v
  UNION ALL
  SELECT 'low_income (รายได้ครึ่งล่าง)', district_code, flag, flooded FROM income_half
),
overall AS (
  SELECT feature,
         CAST(SUM(flag) AS DOUBLE)                  AS n1,
         CAST(SUM(1 - flag) AS DOUBLE)              AS n0,
         CAST(SUM(flag * flooded) AS DOUBLE)        AS x1,
         CAST(SUM((1 - flag) * flooded) AS DOUBLE)  AS x0
  FROM base
  GROUP BY feature
),
by_district AS (
  SELECT feature, district_code,
         CAST(SUM(flag) AS DOUBLE)                  AS n1,
         CAST(SUM(1 - flag) AS DOUBLE)              AS n0,
         CAST(SUM(flag * flooded) AS DOUBLE)        AS x1,
         CAST(SUM((1 - flag) * flooded) AS DOUBLE)  AS x0
  FROM base
  GROUP BY feature, district_code
),
stratified AS (
  SELECT feature,
         SUM((n1 * n0 / (n1 + n0)) * (x1 / n1 - x0 / n0)) / SUM(n1 * n0 / (n1 + n0)) AS diff,
         COUNT(*) AS districts_compared
  FROM by_district
  WHERE n1 > 0 AND n0 > 0
  GROUP BY feature
)
SELECT
  o.feature,
  CAST(o.n1 AS BIGINT) AS villages_with,
  CAST(o.n0 AS BIGINT) AS villages_without,
  ROUND(100 * o.x1 / o.n1, 1) AS pct_flooded_with,
  ROUND(100 * o.x0 / o.n0, 1) AS pct_flooded_without,
  ROUND(100 * (o.x1 / o.n1 - o.x0 / o.n0), 1) AS diff_pp,
  ROUND((o.x1 / o.n1 - o.x0 / o.n0)
        / SQRT(((o.x1 + o.x0) / (o.n1 + o.n0)) * (1 - (o.x1 + o.x0) / (o.n1 + o.n0)) * (1 / o.n1 + 1 / o.n0)), 2) AS z,
  ROUND(100 * s.diff, 1) AS within_district_diff_pp,
  s.districts_compared
FROM overall o
JOIN stratified s ON s.feature = o.feature
ORDER BY o.feature;
