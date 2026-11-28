BUCKET = "cs341-flood-recovery"
REGION = "us-east-1"

# local_file -> ปลายทางใน S3 (s3_prefix + s3_name)
# คงชื่อคีย์เหล่านี้ไว้ เพราะ orchestration/lambda_handlers.py และ prepare_local_data.py ใช้งานอยู่
# source / source_url / period ถูกบันทึกลง manifest ทุกครั้งที่รัน ingest.py
# รายละเอียดเต็ม (คอลัมน์ ช่วงเวลา ข้อจำกัด) อยู่ที่ data_catalog/sources.md
# source_url = "" หมายถึงทีมได้ไฟล์มาโดยตรง ไม่มีหน้าเผยแพร่สาธารณะ (ดู source และ data_catalog/sources.md หัวข้อ 3)

FILES = [
    {
        "local_file": "flood_2566.csv",
        "s3_prefix": "raw/pdpm/flood_stats/",
        "s3_name": "flood_2566.csv",
        "source": "กรมป้องกันและบรรเทาสาธารณภัย (ปภ.) ชุดข้อมูล dpm-gd027 สถิติรายปีการเกิดอุทกภัย ไฟล์ปี 2566 (CSV)",
        "source_url": "https://catalog.disaster.go.th/dataset/dpm-gd027/resource/af2370d1-d2d0-4844-a16d-e6af34926e71",
        "period": "วันเกิดภัย 14 ม.ค.-28 ธ.ค. 2566 (ค.ศ. 2023) 69 จังหวัด",
    },
    {
        "local_file": "flood_2567.csv",
        "s3_prefix": "raw/pdpm/flood_stats/",
        "s3_name": "flood_2567.csv",
        "source": "กรมป้องกันและบรรเทาสาธารณภัย (ปภ.) ชุดข้อมูล dpm-gd027 สถิติรายปีการเกิดอุทกภัย ไฟล์ปี 2567 (ต้นทางเป็น XLSX บันทึกเป็น CSV)",
        "source_url": "https://catalog.disaster.go.th/dataset/dpm-gd027/resource/dde2eddc-28f5-40bf-8a62-28bc68f02af8",
        "period": "วันเกิดภัย 16 ม.ค.-29 ธ.ค. 2567 (ค.ศ. 2024) 72 จังหวัด",
    },
    {
        "local_file": "chiangmai_damage.xlsx",
        "s3_prefix": "raw/pdpm/flood_stats/",
        "s3_name": "chiangmai_damage.xlsx",
        "source": "ข้อมูลความเสียหายจากอุทกภัยรายหมู่บ้าน จังหวัดเชียงใหม่ (ทีมได้รับเป็นไฟล์ XLSX ไม่มีลิงก์สาธารณะ ยังไม่ได้ยืนยันหน่วยงานเจ้าของข้อมูล)",
        "source_url": "",
        "period": "ปี 2563-2567 (ค.ศ. 2020-2024) จังหวัดเชียงใหม่ 25 อำเภอ",
    },
    {
        "local_file": "household_income.xlsx",
        "s3_prefix": "raw/nso/",
        "s3_name": "household_income.xlsx",
        "source": "รายได้ครัวเรือนเฉลี่ยรายหมู่บ้าน (บาท/ปี) จังหวัดเชียงใหม่ (ทีมได้รับเป็นไฟล์ XLSX ไม่มีลิงก์สาธารณะ ยังไม่ได้ยืนยันหน่วยงานเจ้าของข้อมูล)",
        "source_url": "",
        "period": "ไม่ระบุปีในไฟล์ จังหวัดเชียงใหม่ 25 อำเภอ",
    },
    {
        "local_file": "village_mapping.json",
        "s3_prefix": "raw/dopa/",
        "s3_name": "village_mapping.json",
        "source": "ข้อมูลพื้นฐานรายหมู่บ้าน จังหวัดเชียงใหม่ (รหัสหมู่บ้าน พิกัด ประชากร ลักษณะภูมิศาสตร์ คอลัมน์ oct_side15_*) ทีมได้รับเป็นไฟล์ JSON ไม่มีลิงก์สาธารณะ",
        "source_url": "",
        "period": "ไม่ระบุปีในไฟล์ จังหวัดเชียงใหม่ 2,198 แถว (25 อำเภอ 204 ตำบล)",
    },
]
