BUCKET = "cs341-flood-recovery"
REGION = "us-east-1"

# เติมหลังตรวจไฟล์แล้ว: local_file -> ปลายทางใน S3

FILES = [
    {
        "local_file": "STATISTIC_FLD.xlsx",
        "s3_prefix": "raw/pdpm/flood_stats/",
        "s3_name": "pdpm_flood_village_stats.xlsx",
        "source": "ปภ. สถิติอุทกภัยรายหมู่บ้าน",
        "source_url": "https://drive.disaster.go.th/index.php/s/g8xpZR8TSWitRYf",
    },
    {
        "local_file": "dpm-gd015__1.csv",
        "s3_prefix": "raw/pdpm/flood_stats/",       # TODO: ยืนยันหลังตรวจไฟล์
        "s3_name": "pdpm_gd015.csv",
        "source": "TODO: ระบุชื่อชุดข้อมูล",
        "source_url": "TODO",
    },
    {
        "local_file": "2564_by_disaster_type1.csv",
        "s3_prefix": "raw/pdpm/flood_stats/",       # TODO
        "s3_name": "pdpm_2564_by_disaster_type.csv",
        "source": "TODO",
        "source_url": "TODO",
    },
    {
        "local_file": "Number_of_Affected_Households.xlsx",
        "s3_prefix": "raw/pdpm/flood_relief/",      # TODO: อาจเป็น compensation
        "s3_name": "pdpm_affected_households.xlsx",
        "source": "TODO",
        "source_url": "TODO",
    },
    {
        "local_file": "Salary.csv",
        "s3_prefix": "raw/nso/",
        "s3_name": "nso_household_income.csv",
        "source": "TODO",
        "source_url": "TODO",
    },

]