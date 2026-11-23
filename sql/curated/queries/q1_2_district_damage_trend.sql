-- Q1.2 รูปแบบความเสียหายรายปีในแต่ละอำเภอ 2563-2567 (ข้อมูลความเสียหาย ค่าครบทุกแถว)
-- แสดง 10 อำเภอที่มีครัวเรือนได้รับผลกระทบรวมสูงสุด แยกตามปี
WITH totals AS (
  SELECT district_code, SUM(affected_households) AS hh_all_years
  FROM flood_recovery_db.fact_disaster_damage
  GROUP BY district_code
),
top10 AS (
  SELECT district_code FROM totals ORDER BY hh_all_years DESC LIMIT 10
)
SELECT
  d.district,
  d.source_year,
  COUNT(*)                                   AS damage_records,
  SUM(d.affected_households)                 AS affected_households,
  SUM(d.affected_people)                     AS affected_people,
  SUM(d.houses_damaged)             AS houses_damaged,
  SUM(d.partially_damaged_houses)   AS partially_damaged_houses
FROM flood_recovery_db.fact_disaster_damage d
JOIN top10 t ON d.district_code = t.district_code
GROUP BY d.district, d.source_year
ORDER BY d.district, d.source_year;
