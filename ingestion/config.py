BUCKET = "cs341-flood-recovery"
REGION = "us-east-1"

# local_file -> ปลายทางใน S3 (s3_prefix + s3_name)
# คงชื่อคีย์เหล่านี้ไว้ เพราะ orchestration/lambda_handlers.py ใช้งานอยู่
# source_url เว้นว่างไว้เมื่อยังไม่มี URL ต้นทางที่ยืนยันได้

FILES = [
    {
        "local_file": "flood_2566.csv",
        "s3_prefix": "raw/pdpm/flood_stats/",
        "s3_name": "flood_2566.csv",
        "source": "กรมป้องกันและบรรเทาสาธารณภัย (ปภ.): สถิติรายปีการเกิดอุทกภัย พ.ศ. 2566",
        "source_url": "",
    },
    {
        "local_file": "flood_2567.csv",
        "s3_prefix": "raw/pdpm/flood_stats/",
        "s3_name": "flood_2567.csv",
        "source": "กรมป้องกันและบรรเทาสาธารณภัย (ปภ.): สถิติรายปีการเกิดอุทกภัย พ.ศ. 2567",
        "source_url": "",
    },
    {
        "local_file": "chiangmai_damage.xlsx",
        "s3_prefix": "raw/pdpm/flood_stats/",
        "s3_name": "chiangmai_damage.xlsx",
        "source": "ข้อมูลความเสียหายจากอุทกภัย จังหวัดเชียงใหม่ (ไฟล์ที่ผู้ใช้นำเข้ามา)",
        "source_url": "",
    },
    {
        "local_file": "household_income.xlsx",
        "s3_prefix": "raw/nso/",
        "s3_name": "household_income.xlsx",
        "source": "ข้อมูลรายได้ครัวเรือนรายพื้นที่ (ไฟล์ที่ผู้ใช้นำเข้ามา)",
        "source_url": "",
    },
    {
        "local_file": "village_mapping.json",
        "s3_prefix": "raw/dopa/",
        "s3_name": "village_mapping.json",
        "source": "กรมการปกครอง (DOPA): ข้อมูลขอบเขตและรายละเอียดหมู่บ้าน",
        "source_url": "",
    },
]
