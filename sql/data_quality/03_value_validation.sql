-- CS341 Flood Impact & Recovery
-- Data Quality: Value Validation
-- Database: flood_recovery_db

-- 34. ตรวจสอบค่าติดลบ ค่าศูนย์ และค่าบวกใน NSO Income
SELECT
    COUNT(*) AS total_records,
    COUNT_IF(value < 0) AS negative_values,
    COUNT_IF(value = 0) AS zero_values,
    COUNT_IF(value > 0) AS positive_values,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    ROUND(AVG(value), 2) AS average_value
FROM nso_income;