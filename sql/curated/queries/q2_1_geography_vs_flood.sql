-- Q2.1 ลักษณะทางภูมิศาสตร์สัมพันธ์กับการถูกรายงานน้ำท่วมหรือไม่
-- เทียบสัดส่วนหมู่บ้านที่ถูกรายงานน้ำท่วม (อย่างน้อย 1 ครั้งในปี 2566-2567)
-- ระหว่างหมู่บ้านที่ "มี" กับ "ไม่มี" ลักษณะนั้น (flag = 1 / 0)
-- เป็นความสัมพันธ์เชิงพรรณนา ไม่ใช่เหตุและผล
WITH p AS (SELECT * FROM flood_recovery_db.v_village_profile),
features AS (
  SELECT 'river (แม่น้ำ/ลำน้ำ)' AS feature, river_flag     AS flag, reports_total FROM p
  UNION ALL SELECT 'mountain (ภูเขา)',       mountain_flag,  reports_total FROM p
  UNION ALL SELECT 'swamp (หนอง/บึง)',       swamp_flag,     reports_total FROM p
  UNION ALL SELECT 'dam (เขื่อน)',            dam_flag,       reports_total FROM p
  UNION ALL SELECT 'reservoir (อ่างเก็บน้ำ)', reservoir_flag, reports_total FROM p
)
SELECT
  feature,
  flag,
  COUNT(*) AS villages,
  SUM(CASE WHEN reports_total > 0 THEN 1 ELSE 0 END) AS villages_flooded,
  ROUND(100.0 * SUM(CASE WHEN reports_total > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_flooded,
  ROUND(AVG(CAST(reports_total AS DOUBLE)), 2) AS avg_reports_per_village
FROM features
WHERE flag IS NOT NULL
GROUP BY feature, flag
ORDER BY feature, flag;