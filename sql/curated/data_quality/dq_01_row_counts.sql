-- DQ1: row count per table / partition. Expected (storage/reports/curated_build_report.json):
-- dim_village 2184 | fact_flood_report 2566=1198, 2567=3556 | fact_disaster_damage 866 | fact_household_income 2154
SELECT 'dim_village' AS table_name, CAST(NULL AS INTEGER) AS source_year, COUNT(*) AS row_count FROM flood_recovery_db.dim_village
UNION ALL
SELECT 'fact_flood_report', source_year, COUNT(*) FROM flood_recovery_db.fact_flood_report GROUP BY source_year
UNION ALL
SELECT 'fact_disaster_damage', source_year, COUNT(*) FROM flood_recovery_db.fact_disaster_damage GROUP BY source_year
UNION ALL
SELECT 'fact_household_income', CAST(NULL AS INTEGER), COUNT(*) FROM flood_recovery_db.fact_household_income
ORDER BY table_name, source_year;
