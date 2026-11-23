-- DQ2: primary keys must be unique and not null. Expect duplicate_keys = 0 and null_keys = 0 everywhere.
SELECT 'dim_village' AS table_name,
       COUNT(*) - COUNT(DISTINCT village_code) AS duplicate_keys,
       SUM(CASE WHEN village_code IS NULL THEN 1 ELSE 0 END) AS null_keys
FROM flood_recovery_db.dim_village
UNION ALL
SELECT 'fact_flood_report',
       COUNT(*) - COUNT(DISTINCT CAST(source_year AS VARCHAR) || '|' || source_record_id),
       SUM(CASE WHEN source_record_id IS NULL THEN 1 ELSE 0 END)
FROM flood_recovery_db.fact_flood_report
UNION ALL
SELECT 'fact_disaster_damage',
       COUNT(*) - COUNT(DISTINCT source_record_id),
       SUM(CASE WHEN source_record_id IS NULL THEN 1 ELSE 0 END)
FROM flood_recovery_db.fact_disaster_damage
UNION ALL
SELECT 'fact_household_income',
       COUNT(*) - COUNT(DISTINCT income_record_id),
       SUM(CASE WHEN income_record_id IS NULL THEN 1 ELSE 0 END)
FROM flood_recovery_db.fact_household_income;
