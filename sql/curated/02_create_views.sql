-- Serving views on top of the curated tables (Person 4).
-- Village attributes live only in dim_village; the views join them at query
-- time instead of copying them into every fact table.
-- Works in Athena (Trino) and in DuckDB (storage/run_local_queries.py).

-- 1) Flood report + village attributes. village_found = 0 marks the 33 flood
--    rows whose village_code is not in dim_village (kept, not dropped).
CREATE OR REPLACE VIEW flood_recovery_db.v_flood_report_village AS
SELECT
  f.source_year,
  f.source_record_id,
  f.disaster_date,
  f.district_code,
  f.district,
  f.subdistrict_code,
  f.subdistrict,
  f.village_code,
  f.cause,
  f.affected_people,
  f.affected_households,
  f.housing_damage,
  f.agriculture_damage,
  CASE WHEN v.village_code IS NULL THEN 0 ELSE 1 END AS village_found,
  v.village_name,
  v.latitude,
  v.longitude,
  v.population_total,
  v.households,
  v.river_flag,
  v.mountain_flag,
  v.swamp_flag,
  v.dam_flag,
  v.reservoir_flag
FROM flood_recovery_db.fact_flood_report f
LEFT JOIN flood_recovery_db.dim_village v
  ON f.village_code = v.village_code;

-- 2) One row per village in dim_village: how often it was reported flooded
--    (2566-2567), plus geography, population and average household income.
--    Income is attached only for unique_match rows; ambiguous/unmatched stay NULL.
CREATE OR REPLACE VIEW flood_recovery_db.v_village_profile AS
WITH flood AS (
  SELECT
    village_code,
    SUM(CASE WHEN source_year = 2566 THEN 1 ELSE 0 END) AS reports_2566,
    SUM(CASE WHEN source_year = 2567 THEN 1 ELSE 0 END) AS reports_2567,
    COUNT(*)                                            AS reports_total,
    COUNT(DISTINCT source_year)                         AS years_flooded,
    SUM(affected_households)                            AS reported_affected_households
  FROM flood_recovery_db.fact_flood_report
  GROUP BY village_code
),
income AS (
  SELECT
    village_code,
    AVG(CAST(avg_household_income_baht_per_year AS DOUBLE)) AS avg_household_income
  FROM flood_recovery_db.fact_household_income
  WHERE mapping_match_status = 'unique_match'
  GROUP BY village_code
)
SELECT
  v.village_code,
  v.village_name,
  v.district_code,
  v.district_name,
  v.subdistrict_code,
  v.subdistrict_name,
  v.latitude,
  v.longitude,
  v.population_total,
  v.households,
  v.river_flag,
  v.mountain_flag,
  v.swamp_flag,
  v.dam_flag,
  v.reservoir_flag,
  COALESCE(f.reports_2566, 0)  AS reports_2566,
  COALESCE(f.reports_2567, 0)  AS reports_2567,
  COALESCE(f.reports_total, 0) AS reports_total,
  COALESCE(f.years_flooded, 0) AS years_flooded,
  f.reported_affected_households,
  i.avg_household_income
FROM flood_recovery_db.dim_village v
LEFT JOIN flood f ON f.village_code = v.village_code
LEFT JOIN income i ON i.village_code = v.village_code;
