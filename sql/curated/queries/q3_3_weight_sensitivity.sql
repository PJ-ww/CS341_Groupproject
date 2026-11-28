-- Q3.3 Sensitivity ของน้ำหนักคะแนนใน q3_1: เปลี่ยนน้ำหนักแล้ว top 30 / top 10 หมู่บ้านเปลี่ยนไปเท่าไร
-- ใช้สูตรและองค์ประกอบเดียวกับ q3_1 (PERCENT_RANK, รายได้ที่ไม่มีข้อมูลใช้ 0.5)
-- จัดลำดับด้วย ROW_NUMBER (ตัดเสมอด้วย village_code) เพื่อให้ top N มีจำนวนคงที่และผลซ้ำได้
-- rank_corr = Pearson correlation ของลำดับ (= Spearman) เทียบกับชุด baseline บนหมู่บ้านที่ถูกรายงานทั้งหมด
WITH flooded AS (
  SELECT * FROM flood_recovery_db.v_village_profile WHERE reports_total > 0
),
scored AS (
  SELECT
    village_code,
    PERCENT_RANK() OVER (ORDER BY reports_total)           AS s_flood,
    PERCENT_RANK() OVER (ORDER BY COALESCE(households, 0)) AS s_exposure,
    CASE WHEN avg_household_income IS NULL THEN NULL
         ELSE 1 - PERCENT_RANK() OVER (
                    PARTITION BY CASE WHEN avg_household_income IS NULL THEN 0 ELSE 1 END
                    ORDER BY avg_household_income)
    END AS s_low_income
  FROM flooded
),
weights AS (
  SELECT * FROM (VALUES
    ('1 baseline 0.5/0.3/0.2',        0.5,   0.3,   0.2),
    ('2 equal 1/3 each',              0.334, 0.333, 0.333),
    ('3 flood-heavy 0.7/0.2/0.1',     0.7,   0.2,   0.1),
    ('4 exposure-heavy 0.3/0.5/0.2',  0.3,   0.5,   0.2),
    ('5 income-heavy 0.4/0.2/0.4',    0.4,   0.2,   0.4),
    ('6 flood only 1/0/0',            1.0,   0.0,   0.0)
  ) AS t (weight_set, w_flood, w_exposure, w_income)
),
ranked AS (
  SELECT w.weight_set, w.w_flood, w.w_exposure, w.w_income, s.village_code,
         ROW_NUMBER() OVER (
           PARTITION BY w.weight_set
           ORDER BY w.w_flood * s.s_flood + w.w_exposure * s.s_exposure
                    + w.w_income * COALESCE(s.s_low_income, 0.5) DESC,
                    s.village_code) AS rn
  FROM weights w CROSS JOIN scored s
),
base AS (
  SELECT village_code, rn AS base_rn FROM ranked WHERE weight_set = '1 baseline 0.5/0.3/0.2'
)
SELECT
  r.weight_set,
  r.w_flood, r.w_exposure, r.w_income,
  SUM(CASE WHEN r.rn <= 30 AND b.base_rn <= 30 THEN 1 ELSE 0 END) AS top30_overlap_with_baseline,
  SUM(CASE WHEN r.rn <= 10 AND b.base_rn <= 10 THEN 1 ELSE 0 END) AS top10_overlap_with_baseline,
  ROUND(CORR(CAST(r.rn AS DOUBLE), CAST(b.base_rn AS DOUBLE)), 3) AS rank_corr_with_baseline,
  COUNT(*) AS villages_ranked
FROM ranked r
JOIN base b ON b.village_code = r.village_code
GROUP BY r.weight_set, r.w_flood, r.w_exposure, r.w_income
ORDER BY r.weight_set;
