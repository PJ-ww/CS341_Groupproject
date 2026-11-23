-- Q3.2 สรุประดับอำเภอ: ใช้วางแผนจัดสรรทรัพยากรภาพรวม
-- รวมหลักฐาน 3 ด้าน: หมู่บ้านที่ถูกรายงานน้ำท่วม (2566-2567), ครัวเรือนได้รับผลกระทบจากข้อมูลความเสียหาย (2563-2567),
-- และรายได้ครัวเรือนเฉลี่ยของหมู่บ้านที่จับคู่ได้
WITH village AS (
  SELECT district_code, district_name,
         COUNT(*) AS villages,
         SUM(CASE WHEN reports_total > 0 THEN 1 ELSE 0 END) AS villages_flooded,
         SUM(CASE WHEN years_flooded = 2 THEN 1 ELSE 0 END) AS villages_flooded_both_years,
         SUM(households) AS households,
         AVG(avg_household_income) AS avg_household_income
  FROM flood_recovery_db.v_village_profile
  GROUP BY district_code, district_name
),
damage AS (
  SELECT district_code,
         SUM(affected_households) AS damage_affected_households_2563_2567,
         COUNT(DISTINCT source_year) AS damage_years
  FROM flood_recovery_db.fact_disaster_damage
  GROUP BY district_code
)
SELECT
  v.district_name,
  v.villages,
  v.villages_flooded,
  ROUND(100.0 * v.villages_flooded / v.villages, 1) AS pct_villages_flooded,
  v.villages_flooded_both_years,
  COALESCE(d.damage_affected_households_2563_2567, 0) AS damage_affected_households_2563_2567,
  COALESCE(d.damage_years, 0) AS damage_years,
  ROUND(v.avg_household_income, 0) AS avg_household_income,
  RANK() OVER (ORDER BY 100.0 * v.villages_flooded / v.villages DESC) AS rank_by_flood_share,
  RANK() OVER (ORDER BY COALESCE(d.damage_affected_households_2563_2567, 0) DESC) AS rank_by_damage
FROM village v
LEFT JOIN damage d ON v.district_code = d.district_code
ORDER BY rank_by_flood_share + rank_by_damage, v.district_name;
