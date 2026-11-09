-- CS341 Flood Impact & Recovery
-- Data Quality: Duplicate Checks
-- Database: flood_recovery_db

-- 26. ตรวจสอบข้อมูลซ้ำทั้งแถวใน geographic
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT ROW(
        "ปี", "รายการ", "อำเภอ", "ตำบล", "หมู่ที่",
        "ความเสี่ยง", "เหล่งที่มา", risk_level_code, risk_level
    )) AS distinct_rows
FROM geographic;


-- 27. ตรวจสอบข้อมูลซ้ำทั้งแถวใน flood_village_stats
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT ROW(
        province_code, province_name,
        amphur_code, amphur_name,
        district_code, district_name,
        moo_no, org_code, org_name,
        community_name, moo_id, dis_type_name,
        y2562, y2563, y2564, y2565, y2566, y2567,
        years_with_reported_value
    )) AS distinct_rows
FROM flood_village_stats;


-- 28. ตรวจสอบข้อมูลซ้ำทั้งแถวใน nso_income
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT ROW(
        year, province,
        source_income1, source_income2, source_income3,
        soc_eco_class1, soc_eco_class2,
        value, unit, attribute, source
    )) AS distinct_rows
FROM nso_income;


-- 29. ตรวจสอบข้อมูลซ้ำทั้งแถวใน disaster_budget
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT ROW(
        "ปี", "ที่", "จังหวัด",
        "ด้านดำรงชีพ", "ด้านสังคมสงเคราะห์", "ด้านการแพทย์",
        "ด้านเกษตรพืช", "ด้านเกษตรประมง",
        "ด้านเกษตรปศุสัตว์", "ด้านเกษตรอื่น",
        "ด้านบรรเทา", "ด้านการปฏิบัติงานให้",
        "ป้องกันหรือยับยั้ง", "รวมทั้งสิ้น",
        "วงเงิน", "วงเงินอนุมัติ", "วงเงินไม่อนุมัติ"
    )) AS distinct_rows
FROM disaster_budget;


-- 30. ตรวจสอบข้อมูลซ้ำทั้งแถวใน flood_affected_households
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT ROW(
        "ปี", "รายการ", "อำเภอ", "ตำบล",
        "จำนวน", "หน่วย", "ที่มา"
    )) AS distinct_rows
FROM flood_affected_households;


-- 31. ตรวจสอบข้อมูลซ้ำทั้งแถวใน affected_households_summary
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT ROW(
        "ครั้งที่", "อำเภอ", "รายการ", "จำนวน", "หน่วยนับ"
    )) AS distinct_rows
FROM affected_households_summary;


-- 32. ตรวจสอบข้อมูลซ้ำทั้งแถวใน geographic_nso_integrated
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT ROW(
        "จังหวัด", "ปี", income_indicator, socioeconomic_group,
        monthly_income_value, income_unit, geographic_area_records,
        risk_very_low_count, risk_low_count, risk_moderate_count,
        risk_high_count, risk_very_high_count,
        risk_very_low_pct, risk_low_pct, risk_moderate_pct,
        risk_high_pct, risk_very_high_pct
    )) AS distinct_rows
FROM geographic_nso_integrated;