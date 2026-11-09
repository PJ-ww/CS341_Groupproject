-- CS341 Flood Impact & Recovery
-- Disaster Budget Analysis
-- Database: flood_recovery_db

-- 08. งบประมาณแยกตามจังหวัด ปี 2564
SELECT
    "จังหวัด" AS province,
    COUNT(*) AS total_records,
    ROUND(SUM("วงเงิน"), 2) AS total_budget,
    ROUND(SUM("วงเงินอนุมัติ"), 2) AS total_approved,
    ROUND(SUM("รวมทั้งสิ้น"), 2) AS total_reported
FROM disaster_budget
WHERE "ปี" = 2564
GROUP BY "จังหวัด"
ORDER BY total_approved DESC NULLS LAST;


-- 09. รายละเอียดงบประมาณรายหมวดของจังหวัดยโสธร ปี 2564
SELECT
    "จังหวัด" AS province,
    "ปี" AS year,
    "ด้านดำรงชีพ" AS livelihood,
    "ด้านสังคมสงเคราะห์" AS social_welfare,
    "ด้านการแพทย์" AS medical,
    "ด้านเกษตรพืช" AS crop,
    "ด้านเกษตรประมง" AS fishery,
    "ด้านเกษตรปศุสัตว์" AS livestock,
    "ด้านเกษตรอื่น" AS other_agriculture,
    "ด้านบรรเทา" AS relief,
    "ด้านการปฏิบัติงานให้" AS operation,
    "ป้องกันหรือยับยั้ง" AS prevention,
    "รวมทั้งสิ้น" AS total_reported,
    "วงเงิน" AS budget,
    "วงเงินอนุมัติ" AS approved,
    "วงเงินไม่อนุมัติ" AS rejected
FROM disaster_budget
WHERE "จังหวัด" = 'ยโสธร'
  AND "ปี" = 2564;