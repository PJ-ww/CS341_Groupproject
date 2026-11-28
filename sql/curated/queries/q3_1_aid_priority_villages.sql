-- Q3.1 จัดลำดับความสำคัญของหมู่บ้านเพื่อวางแผนช่วยเหลือ (rule-based, โปร่งใส ปรับน้ำหนักได้)
-- คะแนน = 0.5 * ความถี่น้ำท่วม + 0.3 * จำนวนครัวเรือน (exposure) + 0.2 * รายได้ต่ำ (vulnerability)
-- แต่ละองค์ประกอบใช้ PERCENT_RANK (0-1) ให้อยู่สเกลเดียวกัน
-- หมู่บ้านที่ไม่มีข้อมูลรายได้ (จับคู่ไม่ได้) ให้ค่ากลาง 0.5 และติดธง income_available = 0
-- น้ำหนัก 0.5/0.3/0.2 เป็นข้อตกลงของทีม: ความถี่เป็นตัวชี้วัดผลกระทบตัวเดียวที่ครบทุกหมู่บ้าน, ครัวเรือนคือขนาดที่ต้องช่วย,
-- รายได้ให้น้ำหนักต่ำสุดเพราะจับคู่ได้ 67% และไม่มีปี (เหตุผลเต็มใน docs/07-findings-and-interpretation.md หัวข้อ 7.3)
-- น้ำหนักเปลี่ยนได้: ดูผลเมื่อเปลี่ยนน้ำหนักใน q3_3_weight_sensitivity.sql (rank correlation 0.83-0.96 กับชุดอื่น)
WITH flooded AS (
  SELECT * FROM flood_recovery_db.v_village_profile WHERE reports_total > 0
),
scored AS (
  SELECT
    village_code, village_name, district_name, subdistrict_name,
    reports_total, years_flooded, households, avg_household_income,
    PERCENT_RANK() OVER (ORDER BY reports_total)            AS s_flood,
    PERCENT_RANK() OVER (ORDER BY COALESCE(households, 0))  AS s_exposure,
    CASE WHEN avg_household_income IS NULL THEN NULL
         ELSE 1 - PERCENT_RANK() OVER (
                    PARTITION BY CASE WHEN avg_household_income IS NULL THEN 0 ELSE 1 END
                    ORDER BY avg_household_income)
    END AS s_low_income
  FROM flooded
)
SELECT
  RANK() OVER (ORDER BY 0.5 * s_flood + 0.3 * s_exposure + 0.2 * COALESCE(s_low_income, 0.5) DESC) AS priority_rank,
  village_code, village_name, district_name, subdistrict_name,
  reports_total, years_flooded, households,
  ROUND(avg_household_income, 0) AS avg_household_income,
  CASE WHEN s_low_income IS NULL THEN 0 ELSE 1 END AS income_available,
  ROUND(0.5 * s_flood + 0.3 * s_exposure + 0.2 * COALESCE(s_low_income, 0.5), 3) AS priority_score
FROM scored
ORDER BY priority_rank, village_code
LIMIT 30;
