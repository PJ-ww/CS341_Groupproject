<<<<<<< Updated upstream
# Ingestion and validation

- `inspect_files.py` แสดงหัวตารางและตัวอย่างข้อมูลจาก CSV/XLSX (ต้องติดตั้ง `openpyxl`)
- `validate_data.py` ตรวจเงื่อนไขคุณภาพพื้นฐานจากไฟล์ใน `data/` โดยไม่แก้ raw และแยกผลไว้ที่ root ของ repo ใน `validation/reports/`, `validation/cleaned/` และ `validation/quarantine/`
- ดูวิธีตรวจ กฎ และผลล่าสุดใน [`docs/04-data-validation.md`](../docs/04-data-validation.md)

รัน validator จาก root ของ repo:

```powershell
python ingestion/validate_data.py
```
=======
# Installation and AWS Configuration

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
source .venv/bin/activate
```

ติดตั้ง Python dependencies:

```bash
python -m pip install -r ingestion/requirements.txt
```

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

ดาวน์โหลด Dataset ทั้ง 8 ไฟล์จาก S3:

```bash
aws s3 cp s3://cs341-flood-recovery/raw/pdpm/flood_stats/pdpm_flood_village_stats.xlsx ingestion/data/STATISTIC_FLD.xlsx --profile cs341-team

aws s3 cp s3://cs341-flood-recovery/raw/pdpm/flood_stats/pdpm_gd015.csv ingestion/data/dpm-gd015__1.csv --profile cs341-team

aws s3 cp s3://cs341-flood-recovery/raw/pdpm/flood_stats/pdpm_2564_by_disaster_type.csv ingestion/data/2564_by_disaster_type1.csv --profile cs341-team

aws s3 cp s3://cs341-flood-recovery/raw/pdpm/flood_relief/pdpm_affected_households.xlsx ingestion/data/Number_of_Affected_Households.xlsx --profile cs341-team

aws s3 cp s3://cs341-flood-recovery/raw/nso/nso_household_income.csv ingestion/data/Salary.csv --profile cs341-team

aws s3 cp s3://cs341-flood-recovery/raw/pdpm/geographic/pdpm_flood_risk_geographic.csv ingestion/data/Geographic_Data.csv --profile cs341-team

aws s3 cp s3://cs341-flood-recovery/raw/pdpm/flood_relief/pdpm_flood_affected_households.csv "ingestion/data/Number_of Households_Affected_by_Flooding.csv" --profile cs341-team

aws s3 cp s3://cs341-flood-recovery/raw/nso/nso_household_income_by_area.csv ingestion/data/Salary2.csv --profile cs341-team
```

## 7. Verify Downloaded Files

ตรวจสอบว่า Dataset ถูกดาวน์โหลดครบทั้ง 8 ไฟล์:

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
| Number of Datasets | 8 |

เมื่อดำเนินการครบทุกขั้นตอนแล้ว สมาชิกจะมีโค้ดโปรเจกต์และ Dataset ทั้ง 8 ไฟล์พร้อมสำหรับทำ Data Validation, Data Cleaning และ Data Transformation ต่อไป
>>>>>>> Stashed changes
