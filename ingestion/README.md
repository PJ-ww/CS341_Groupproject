# Ingestion: Installation and AWS Configuration

ขั้นตอนสำหรับสมาชิกในทีมที่ต้องการ Clone โปรเจกต์และดาวน์โหลด Dataset จาก AWS S3 มาใช้งานบนเครื่องของตนเอง โดยสมาชิกทุกคนใช้ AWS IAM User และ Credentials ชุดเดียวกัน

## 1. Prerequisites

ติดตั้งเครื่องมือที่จำเป็นก่อนเริ่มต้นใช้งาน

- Python 3
- AWS CLI Version 2
- Git

**ติดตั้ง AWS CLI บน macOS**

```bash
brew install awscli
```

ตรวจสอบการติดตั้ง:

```bash
aws --version
```

สำหรับ Windows และ Linux ดูวิธีติดตั้งได้จาก [AWS CLI Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

## 2. Clone the Repository

Clone โปรเจกต์จาก GitHub:

```bash
git clone https://github.com/PJ-ww/CS341_Groupproject.git
cd CS341_Groupproject
```

## 3. Set Up Python Environment

สร้าง Virtual Environment:

```bash
python3 -m venv .venv
```

เปิดใช้งาน Virtual Environment:

```bash
source .venv/bin/activate          # macOS / Linux
source .venv/Scripts/activate      # Windows (Git Bash)
.venv\Scripts\Activate.ps1         # Windows (PowerShell)
```

ติดตั้ง Python dependencies ทั้งหมดของโปรเจกต์ (boto3, pandas, pyarrow, openpyxl):

```bash
python -m pip install -r requirements.txt
```

`ingestion/requirements.txt` อ้างถึงไฟล์เดียวกันนี้ ติดตั้งจากไฟล์ไหนก็ได้ผลเหมือนกัน

> **ไม่มี AWS Credentials ของทีม?** (เช่น ผู้ตรวจหรือคนนอกทีม) ข้ามหัวข้อ 4-6 ไปที่หัวข้อ **6B** ด้านล่าง (ใช้ข้อมูลที่ผ่าน validation ซึ่ง commit ไว้แล้ว หรือโหลดไฟล์จากต้นทาง)

## 4. Configure AWS Credentials

สมาชิกทุกคนใช้ AWS IAM User และ Access Key ชุดเดียวกัน ซึ่งเป็น IAM User ที่ได้รับสิทธิ์เข้าถึง S3 Bucket `cs341-flood-recovery`

ผู้ดูแล AWS Account จะต้องจัดเตรียมข้อมูลต่อไปนี้ให้สมาชิก:

- AWS Access Key ID
- AWS Secret Access Key

**หมายเหตุ:** ใช้ Credentials ของ IAM User สำหรับทีมโดยเฉพาะ ห้ามใช้ Root Account Credentials หรือแชร์รหัสผ่าน AWS Console และ MFA

### ตั้งค่า AWS CLI บนเครื่องของสมาชิกแต่ละคน

เปิด Terminal แล้วรันคำสั่ง:

```bash
aws configure --profile cs341-team
```

สมาชิกทุกคนกรอก Credentials ชุดเดียวกัน:

| Field | Value |
|---|---|
| AWS Access Key ID | Access Key ID ของทีม |
| AWS Secret Access Key | Secret Access Key ของทีม |
| Default region name | `us-east-1` |
| Default output format | `json` |

AWS CLI จะสร้างไฟล์ Credentials และ Config ไว้ในเครื่องของสมาชิกแต่ละคนโดยอัตโนมัติ:

```text
~/.aws/credentials
~/.aws/config
```

ตัวอย่างไฟล์ `~/.aws/credentials`:

```ini
[cs341-team]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
```


## 5. Verify AWS Connection

ตรวจสอบ Credentials:

```bash
aws configure list --profile cs341-team
```

ตรวจสอบ AWS Account และ IAM User ที่กำลังใช้งาน:

```bash
aws sts get-caller-identity --profile cs341-team
```

ตรวจสอบการเข้าถึง S3 Bucket:

```bash
aws s3 ls s3://cs341-flood-recovery/raw/ --recursive --profile cs341-team
```

หากสามารถแสดงรายการไฟล์ได้ แสดงว่าเชื่อมต่อ AWS S3 สำเร็จ

## 6. Download Datasets from S3

สร้างโฟลเดอร์สำหรับเก็บข้อมูล:

```bash
mkdir -p ingestion/data
```

ดาวน์โหลด Dataset ทั้ง 5 ไฟล์จาก S3 (S3 key กำหนดไว้ใน [`config.py`](config.py)):

```bash
aws s3 cp s3://cs341-flood-recovery/raw/pdpm/flood_stats/flood_2566.csv ingestion/data/flood_2566.csv --profile cs341-team

aws s3 cp s3://cs341-flood-recovery/raw/pdpm/flood_stats/flood_2567.csv ingestion/data/flood_2567.csv --profile cs341-team

aws s3 cp s3://cs341-flood-recovery/raw/pdpm/flood_stats/chiangmai_damage.xlsx ingestion/data/chiangmai_damage.xlsx --profile cs341-team

aws s3 cp s3://cs341-flood-recovery/raw/nso/household_income.xlsx ingestion/data/household_income.xlsx --profile cs341-team

aws s3 cp s3://cs341-flood-recovery/raw/dopa/village_mapping.json ingestion/data/village_mapping.json --profile cs341-team
```

## 6B. ไม่มี AWS Credentials (ผู้ตรวจหรือคนนอกทีม)

ข้อมูลดิบไม่ได้อยู่ใน Git (`ingestion/data/` อยู่ใน `.gitignore`) รายละเอียดที่มา ช่วงเวลา และข้อจำกัดของแต่ละไฟล์อยู่ใน [`data_catalog/sources.md`](../data_catalog/sources.md)

**ทางที่ง่ายที่สุด: ไม่ต้องใช้ไฟล์ดิบ** `validation/cleaned/*_cleaned.csv` (commit ไว้แล้ว) คือข้อมูลทั้ง 5 ไฟล์หลังผ่าน validation และ `validation/quarantine/` เก็บแถวที่ถูกตัดพร้อมเหตุผล `python run_all.py` เริ่มจากไฟล์เหล่านี้ได้ทันที

ถ้าต้องการรัน validation จากไฟล์ดิบด้วย (`python run_all.py --from-raw`) ให้เตรียมไฟล์ใน `ingestion/data/` โดยไม่สร้างโฟลเดอร์ย่อย:

| # | ไฟล์ | วิธีได้ไฟล์ |
|---|---|---|
| 1 | `flood_2566.csv` | ดาวน์โหลด CSV ปี 2566 จาก ปภ. ชุด `dpm-gd027` สถิติรายปีการเกิดอุทกภัย: https://catalog.disaster.go.th/dataset/dpm-gd027/resource/af2370d1-d2d0-4844-a16d-e6af34926e71 แล้วเปลี่ยนชื่อ |
| 2 | `flood_2567.csv` | ปภ. ชุด `dpm-gd027` ปี 2567: https://catalog.disaster.go.th/dataset/dpm-gd027/resource/dde2eddc-28f5-40bf-8a62-28bc68f02af8 (ต้นทางเป็น XLSX ต้องบันทึกเป็น CSV และต้องมีคอลัมน์ `_id` ดู `data_catalog/sources.md` หัวข้อ 2) |
| 3 | `chiangmai_damage.xlsx` | ไม่มีลิงก์สาธารณะ ขอสำเนาจากทีม |
| 4 | `household_income.xlsx` | ไม่มีลิงก์สาธารณะ ขอสำเนาจากทีม |
| 5 | `village_mapping.json` | ไม่มีลิงก์สาธารณะ ขอสำเนาจากทีม |

โครงสร้างที่ถูกต้องหลังเตรียมครบ:

```text
ingestion/data/
├── chiangmai_damage.xlsx
├── flood_2566.csv
├── flood_2567.csv
├── household_income.xlsx
└── village_mapping.json
```

`inspect_files.py`, `validate_data.py` และ `ingest.py` อ่านไฟล์จากชื่อเหล่านี้ใน `ingestion/data/` โดยตรง (ชื่อกำหนดไว้ที่คีย์ `local_file` ใน [`config.py`](config.py)) ส่วน `prepare_local_data.py` คัดลอกไฟล์ไปไว้ที่ `ingestion/data/raw/...` ตามโครงสร้าง S3 สำหรับกรณีที่ต้องจำลองโฟลเดอร์ทำงานของ Lambda

หมายเหตุ: ข้อมูลบนเว็บต้นทางอาจอัปเดตหลังวันที่ทีมดาวน์โหลด จำนวนแถวจึงอาจไม่ตรงกับตัวเลขใน `data_catalog/sources.md` และรายงานใน repo

## 7. Verify Downloaded Files

ตรวจสอบว่า Dataset ครบทั้ง 5 ไฟล์:

```bash
ls -lh ingestion/data/
```

ตรวจสอบโครงสร้างไฟล์และข้อมูลเบื้องต้น:

```bash
python ingestion/inspect_files.py
```

**AWS S3 Information**

| Item | Value |
|---|---|
| AWS Region | `us-east-1` |
| S3 Bucket | `cs341-flood-recovery` |
| Raw Data Location | `s3://cs341-flood-recovery/raw/` |
| Number of Datasets | 5 |

เมื่อดำเนินการครบทุกขั้นตอนแล้ว สมาชิกจะมีโค้ดโปรเจกต์และ Dataset ทั้ง 5 ไฟล์พร้อมสำหรับทำ Data Validation และ Data Transformation ต่อไป

---

# Data Validation

- `inspect_files.py` แสดงหัวตารางและตัวอย่างข้อมูลจาก CSV/XLSX (ต้องติดตั้ง `openpyxl`)
- `validate_data.py` ตรวจเงื่อนไขคุณภาพพื้นฐานจากไฟล์ใน `data/` โดยไม่แก้ raw และแยกผลไว้ที่ root ของ repo ใน `validation/reports/`, `validation/cleaned/` และ `validation/quarantine/`
- ดูวิธีตรวจ กฎ และผลล่าสุดใน [`docs/04-data-validation.md`](../docs/04-data-validation.md)

รัน validator จาก root ของ repo:

```powershell
python ingestion/validate_data.py
```

---

# Upload Raw Data to S3 (`ingest.py`)

อัปโหลดไฟล์ใน `ingestion/data/` ขึ้น `s3://<BUCKET>/raw/...` ตาม `config.py` (ข้ามไฟล์ที่ md5 ตรงกับใน S3 แล้ว) และเขียน manifest ไว้ที่ `raw/_manifests/` สคริปต์ใช้ default credentials ของ boto3 จึงต้องระบุ profile ผ่านตัวแปรแวดล้อม:

```bash
AWS_PROFILE=cs341-team python ingestion/ingest.py
```

```powershell
$env:AWS_PROFILE = "cs341-team"; python ingestion/ingest.py
```

ขั้นต่อไป (สร้างตาราง Athena, deploy Lambda และ Step Functions) ดูที่ [`orchestration/README.md`](../orchestration/README.md)