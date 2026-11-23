-- DQ3: how well each fact table joins to dim_village.
-- Must reproduce Person 3's integration reports: flood 99.31% matched, income unique_match 67.22%.
SELECT 'fact_flood_report -> dim_village (village_code)' AS relationship,
       COUNT(*) AS fact_rows,
       SUM(CASE WHEN v.village_code IS NOT NULL THEN 1 ELSE 0 END) AS matched_rows,
       ROUND(100.0 * SUM(CASE WHEN v.village_code IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS match_pct
FROM flood_recovery_db.fact_flood_report f
LEFT JOIN flood_recovery_db.dim_village v ON f.village_code = v.village_code
UNION ALL
SELECT 'fact_household_income -> dim_village (unique_match only)',
       COUNT(*),
       SUM(CASE WHEN v.village_code IS NOT NULL THEN 1 ELSE 0 END),
       ROUND(100.0 * SUM(CASE WHEN v.village_code IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2)
FROM flood_recovery_db.fact_household_income i
LEFT JOIN flood_recovery_db.dim_village v ON i.village_code = v.village_code
UNION ALL
SELECT 'fact_disaster_damage -> dim_village (district_code)',
       COUNT(*),
       SUM(CASE WHEN dd.district_code IS NOT NULL THEN 1 ELSE 0 END),
       ROUND(100.0 * SUM(CASE WHEN dd.district_code IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2)
FROM flood_recovery_db.fact_disaster_damage d
LEFT JOIN (SELECT DISTINCT district_code FROM flood_recovery_db.dim_village) dd
  ON d.district_code = dd.district_code;