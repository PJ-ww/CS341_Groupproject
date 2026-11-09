-- CS341 Flood Impact & Recovery
-- Data Quality: NULL Checks
-- Database: flood_recovery_db

-- 33. ตรวจสอบค่า NULL ใน flood_village_stats
SELECT
    COUNT(*) AS total_records,
    COUNT_IF(district_code IS NULL) AS null_district_code,
    COUNT_IF(moo_no IS NULL) AS null_moo_no,
    COUNT_IF(org_code IS NULL) AS null_org_code,
    COUNT_IF(community_name IS NULL) AS null_community_name,
    COUNT_IF(y2562 IS NULL) AS null_y2562,
    COUNT_IF(y2563 IS NULL) AS null_y2563,
    COUNT_IF(y2564 IS NULL) AS null_y2564,
    COUNT_IF(y2565 IS NULL) AS null_y2565,
    COUNT_IF(y2566 IS NULL) AS null_y2566,
    COUNT_IF(y2567 IS NULL) AS null_y2567
FROM flood_village_stats;


-- 35. ตรวจสอบค่า NULL ในคอลัมน์งบประมาณ
SELECT
    COUNT(*) AS total_records,
    COUNT_IF("ด้านดำรงชีพ" IS NULL) AS null_livelihood,
    COUNT_IF("ด้านสังคมสงเคราะห์" IS NULL) AS null_social_welfare,
    COUNT_IF("ด้านการแพทย์" IS NULL) AS null_medical,
    COUNT_IF("ด้านเกษตรพืช" IS NULL) AS null_crop,
    COUNT_IF("ด้านเกษตรประมง" IS NULL) AS null_fishery,
    COUNT_IF("ด้านเกษตรปศุสัตว์" IS NULL) AS null_livestock,
    COUNT_IF("ด้านเกษตรอื่น" IS NULL) AS null_other_agriculture,
    COUNT_IF("ด้านบรรเทา" IS NULL) AS null_relief,
    COUNT_IF("ด้านการปฏิบัติงานให้" IS NULL) AS null_operation,
    COUNT_IF("ป้องกันหรือยับยั้ง" IS NULL) AS null_prevention,
    COUNT_IF("รวมทั้งสิ้น" IS NULL) AS null_total,
    COUNT_IF("วงเงิน" IS NULL) AS null_budget,
    COUNT_IF("วงเงินอนุมัติ" IS NULL) AS null_approved,
    COUNT_IF("วงเงินไม่อนุมัติ" IS NULL) AS null_rejected
FROM disaster_budget;