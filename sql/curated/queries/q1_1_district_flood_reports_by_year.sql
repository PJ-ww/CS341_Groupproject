-- Q1.1 พื้นที่ใด (อำเภอ) ถูกรายงานน้ำท่วมมากที่สุด และเปลี่ยนไปอย่างไรระหว่างปี 2566 -> 2567
-- Metric: จำนวนหมู่บ้านที่ถูกรายงาน (distinct village_code) ต่อปี
-- ใช้จำนวนรายงานแทน affected_households เพราะ affected_households มีค่าแค่ ~9% ของแถว (ดู dq_04)
-- Partition pruning: กรองด้วย source_year ทำให้ Athena อ่านแค่ 2 โฟลเดอร์ปีที่ต้องใช้
WITH by_year AS (
  SELECT district_code, district, source_year,
         COUNT(*)                     AS flood_reports,
         COUNT(DISTINCT village_code) AS villages_reported
  FROM flood_recovery_db.fact_flood_report
  WHERE source_year IN (2566, 2567)
  GROUP BY district_code, district, source_year
)
SELECT
  district_code,
  district,
  SUM(CASE WHEN source_year = 2566 THEN villages_reported ELSE 0 END) AS villages_2566,
  SUM(CASE WHEN source_year = 2567 THEN villages_reported ELSE 0 END) AS villages_2567,
  SUM(CASE WHEN source_year = 2567 THEN villages_reported ELSE 0 END)
    - SUM(CASE WHEN source_year = 2566 THEN villages_reported ELSE 0 END) AS change_villages,
  SUM(flood_reports) AS flood_reports_total
FROM by_year
GROUP BY district_code, district
ORDER BY villages_2567 + villages_2566 DESC
LIMIT 25;
