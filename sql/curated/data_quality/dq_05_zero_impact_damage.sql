-- DQ5: damage records ที่ตัวเลขผลกระทบเป็น 0 ทุกช่อง (มีวันที่เกิดเหตุแต่ไม่มีตัวเลข)
-- พบมากในปี 2567 (54 จาก 182 แถว) เช่น อมก๋อย 12 แถว จึงไม่ควรสรุปว่าความเสียหายลดลงจากตัวเลขรวมรายปี
-- เก็บแถวไว้ตามต้นทาง ไม่ลบหรือเติมค่า แต่แจ้งเป็นข้อจำกัดของข้อมูล
SELECT
  source_year,
  COUNT(*) AS total_records,
  SUM(CASE WHEN COALESCE(affected_people, 0) + COALESCE(affected_households, 0)
              + COALESCE(houses_damaged, 0) + COALESCE(partially_damaged_houses, 0)
              + COALESCE(deaths, 0) + COALESCE(injured_people, 0) = 0
           THEN 1 ELSE 0 END) AS zero_impact_records,
  ROUND(100.0 * SUM(CASE WHEN COALESCE(affected_people, 0) + COALESCE(affected_households, 0)
              + COALESCE(houses_damaged, 0) + COALESCE(partially_damaged_houses, 0)
              + COALESCE(deaths, 0) + COALESCE(injured_people, 0) = 0
           THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_zero_impact
FROM flood_recovery_db.fact_disaster_damage
GROUP BY source_year
ORDER BY source_year;