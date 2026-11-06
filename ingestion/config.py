BUCKET = "cs341-flood-recovery"
REGION = "us-east-1"

SOURCES = [
    {
        "name": "pdpm_flood_stats",
        "url": "https://data.go.th/...ใส่ลิงก์ไฟล์จริง...",
        "s3_prefix": "raw/pdpm/flood_stats/",
        "filename": "flood_stats.csv",
    },
    {
        "name": "pdpm_compensation",
        "url": "https://data.go.th/...",
        "s3_prefix": "raw/pdpm/compensation/",
        "filename": "compensation.xlsx",
    },
    {
        "name": "nso_income",
        "url": "https://data.go.th/...",
        "s3_prefix": "raw/nso/",
        "filename": "income.csv",
    },
]