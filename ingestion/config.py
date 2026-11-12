BUCKET = "cs341-flood-recovery"
REGION = "us-east-1"

# local_file -> ปลายทางใน S3 (s3_prefix + s3_name)
# source / source_url ตรงกับ data_catalog/sources.md และถูกบันทึกลง manifest ทุกครั้งที่รัน
# หมายเหตุ: orchestration/lambda_handlers.py อ่านค่า FILES จากไฟล์นี้ ห้ามเปลี่ยนชื่อคีย์ local_file, s3_prefix, s3_name

FILES = [
    {
        "local_file": "STATISTIC_FLD.xlsx",
        "s3_prefix": "raw/pdpm/flood_stats/",
        "s3_name": "pdpm_flood_village_stats.xlsx",
        "source": "กรมป้องกันและบรรเทาสาธารณภัย (ปภ.): สถิติอุทกภัยรายหมู่บ้าน",
        "source_url": "https://data.go.th/dataset/gdpublish-dfs_21_02",
    },
    {
        "local_file": "dpm-gd015__1.csv",
        "s3_prefix": "raw/pdpm/flood_stats/",
        "s3_name": "pdpm_gd015.csv",
        "source": "กรมป้องกันและบรรเทาสาธารณภัย (ปภ.): สถิติอุทกภัยรายหมู่บ้าน (ชุดย่อย dpm-gd015)",
        "source_url": "https://catalog.disaster.go.th/dataset/dpm-gd015",
    },
    {
        "local_file": "2564_by_disaster_type1.csv",
        "s3_prefix": "raw/pdpm/flood_stats/",
        "s3_name": "pdpm_2564_by_disaster_type.csv",
        "source": "กรมป้องกันและบรรเทาสาธารณภัย (ปภ.): สถิติการให้ความช่วยเหลือผู้ประสบภัยตามระเบียบกระทรวงการคลัง (ด้านการช่วยเหลือ) ปี 2564",
        "source_url": "https://catalog.disaster.go.th/en/dataset/dpm-gd020",
    },
    {
        "local_file": "Number_of_Affected_Households.xlsx",
        "s3_prefix": "raw/pdpm/flood_relief/",
        "s3_name": "pdpm_affected_households.xlsx",
        "source": "data.go.th: จำนวนครัวเรือนที่ได้รับผลกระทบ รายอำเภอ รายครั้ง (disaster_69_14)",
        "source_url": "https://data.go.th/dataset/disaster_69_14",
    },
    {
        "local_file": "Salary.csv",
        "s3_prefix": "raw/nso/",
        "s3_name": "nso_household_income.csv",
        "source": "สำนักงานสถิติแห่งชาติ (NSO): รายได้เฉลี่ยต่อเดือนของครัวเรือน รายจังหวัด",
        "source_url": "https://data.go.th/en/dataset/ns_08_20241",
    },
    {
        "local_file": "Geographic_Data.csv",
        "s3_prefix": "raw/pdpm/geographic/",
        "s3_name": "pdpm_flood_risk_geographic.csv",
        "source": "สำนักงานป้องกันและบรรเทาสาธารณภัยจังหวัด: พื้นที่เสี่ยงน้ำท่วมรายหมู่ที่",
        "source_url": "https://data.go.th",
    },
    {
        "local_file": "Number_of Households_Affected_by_Flooding.csv",
        "s3_prefix": "raw/pdpm/flood_relief/",
        "s3_name": "pdpm_flood_affected_households.csv",
        "source": "สำนักงานท้องถิ่นจังหวัดพังงา: จำนวนครัวเรือนที่ได้รับผลกระทบจากอุทกภัย",
        "source_url": "https://data.go.th/th/dataset/flood01_30",
    },
    {
        "local_file": "Salary2.csv",
        "s3_prefix": "raw/nso/",
        "s3_name": "nso_household_income_by_area.csv",
        "source": "สำนักงานสถิติแห่งชาติ (NSO): รายได้เฉลี่ยต่อเดือนของครัวเรือน รายภาค",
        "source_url": "https://data.go.th/en/dataset/ns_08_20241",
    },
]