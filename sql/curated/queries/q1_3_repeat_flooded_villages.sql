-- Q1.3 หมู่บ้านที่ถูกรายงานน้ำท่วมซ้ำทั้งปี 2566 และ 2567 (พื้นที่เสี่ยงซ้ำซาก)
SELECT
  village_code, village_name, district_name, subdistrict_name,
  reports_2566, reports_2567, reports_total,
  population_total, households, river_flag
FROM flood_recovery_db.v_village_profile
WHERE years_flooded = 2
ORDER BY reports_total DESC, households DESC
LIMIT 20;
