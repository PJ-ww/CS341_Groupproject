-- DQ4: how complete the impact measures are. This decides which metric the analysis can rely on.
SELECT 'fact_flood_report' AS table_name, source_year,
       COUNT(*) AS row_count,
       ROUND(100.0 * COUNT(affected_households) / COUNT(*), 1) AS pct_affected_households_filled,
       ROUND(100.0 * COUNT(affected_people)     / COUNT(*), 1) AS pct_affected_people_filled,
       ROUND(100.0 * COUNT(housing_damage)      / COUNT(*), 1) AS pct_housing_damage_filled
FROM flood_recovery_db.fact_flood_report
GROUP BY source_year
UNION ALL
SELECT 'fact_disaster_damage', source_year,
       COUNT(*),
       ROUND(100.0 * COUNT(affected_households) / COUNT(*), 1),
       ROUND(100.0 * COUNT(affected_people)     / COUNT(*), 1),
       ROUND(100.0 * COUNT(houses_damaged)      / COUNT(*), 1)
FROM flood_recovery_db.fact_disaster_damage
GROUP BY source_year
ORDER BY table_name, source_year;
