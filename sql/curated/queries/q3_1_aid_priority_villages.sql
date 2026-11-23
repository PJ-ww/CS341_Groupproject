-- Q3.1 จัดลำดับความสำคัญของหมู่บ้านเพื่อวางแผนช่วยเหลือ (rule-based, โปร่งใส ปรับน้ำหนักได้)
-- คะแนน = 0.5 * ความถี่น้ำท่วม + 0.3 * จำนวนครัวเรือน (exposure) + 0.2 * รายได้ต่ำ (vulnerability)
-- แต่ละองค์ประกอบใช้ PERCENT_RANK (0-1) ให้อยู่สเกลเดียวกัน
-- หมู่บ้านที่ไม่มีข้อมูลรายได้ (จับคู่ไม่ได้) ให้ค่ากลาง 0.5 และติดธง income_available = 0
-- *** น้ำหนัก 0.5/0.3/0.2 เป็นสมมติฐานของทีม ต้องระบุในรายงานว่าเปลี่ยนได้ ***
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
ORDER BY priority_rank
LIMIT 30;
