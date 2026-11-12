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

> **ไม่มี AWS Credentials ของทีม?** (เช่น ผู้ตรวจหรือคนนอกทีม) ข้ามหัวข้อ 4-6 ไปที่หัวข้อ **6B** ด้านล่าง แล้วโหลดไฟล์จากเว็บไซต์ต้นทางแทน

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

## 6B. ดาวน์โหลดจากแหล่งต้นทาง (ไม่ต้องใช้ AWS)

ข้อมูลดิบไม่ได้อยู่ใน Git (`ingestion/data/` อยู่ใน `.gitignore`) คนที่ไม่มี Credentials ของทีมจึงต้องดาวน์โหลดไฟล์เองจากหน้าชุดข้อมูลด้านล่าง (รายละเอียดเพิ่มเติมอยู่ใน [`data_catalog/sources.md`](../data_catalog/sources.md)) แล้ว**เปลี่ยนชื่อไฟล์ให้ตรงตามคอลัมน์ "บันทึกเป็น"** และวางไว้ในโฟลเดอร์ `ingestion/data/` โดยไม่สร้างโฟลเดอร์ย่อย

| # | หน้าชุดข้อมูล | บันทึกเป็น `ingestion/data/...` |
|---|---|---|
| 1 | https://data.go.th/dataset/gdpublish-dfs_21_02 (ไฟล์ตรง: https://drive.disaster.go.th/index.php/s/g8xpZR8TSWitRYf) | `STATISTIC_FLD.xlsx` |
| 2 | https://catalog.disaster.go.th/dataset/dpm-gd015 | `dpm-gd015__1.csv` |
| 3 | https://catalog.disaster.go.th/en/dataset/dpm-gd020 (ไฟล์ปี 2564 ตามประเภทภัย) | `2564_by_disaster_type1.csv` |
| 4 | https://data.go.th/dataset/disaster_69_14 | `Number_of_Affected_Households.xlsx` |
| 5 | https://data.go.th/th/dataset/flood01_30 | `Number_of Households_Affected_by_Flooding.csv` (มีช่องว่างหลัง `Number_of`) |
| 6 | data.go.th: พื้นที่เสี่ยงน้ำท่วมรายหมู่ที่ จังหวัดยโสธร (สำนักงานป้องกันและบรรเทาสาธารณภัยจังหวัด) | `Geographic_Data.csv` |
| 7 | https://data.go.th/en/dataset/ns_08_20241 (รายได้ครัวเรือน รายจังหวัด) | `Salary.csv` |
| 8 | https://data.go.th/en/dataset/ns_08_20241 (รายได้ครัวเรือน รายภาค) | `Salary2.csv` |

โครงสร้างที่ถูกต้องหลังดาวน์โหลดครบ:

```text
ingestion/data/
├── 2564_by_disaster_type1.csv
├── dpm-gd015__1.csv
├── Geographic_Data.csv
├── Number_of Households_Affected_by_Flooding.csv
├── Number_of_Affected_Households.xlsx
├── Salary.csv
├── Salary2.csv
└── STATISTIC_FLD.xlsx
```

ทุกสคริปต์ (`inspect_files.py`, `validate_data.py`, `ingest.py`, `transformation/scripts/transform_*.py` และ Lambda `ValidateBatch`/`TransformBatch`) อ่านไฟล์จากชื่อเหล่านี้ใน `ingestion/data/` โดยตรง ชื่อไฟล์ทั้งหมดกำหนดไว้ที่คีย์ `local_file` ใน [`config.py`](config.py)

หมายเหตุ

- ข้อมูลบนเว็บต้นทางอาจอัปเดตหลังวันที่ทีมดาวน์โหลด (6 พ.ย. 2569) จำนวนแถวจึงอาจไม่ตรงกับตัวเลขใน `data_catalog/sources.md` และรายงานใน repo
- ถ้าต้องการลองเฉพาะ transformation ฝั่ง geographic (`clean_data.py` → `standardize.py` → `create_features.py`) ไม่ต้องโหลดไฟล์ดิบเลย เพราะสคริปต์เหล่านี้อ่าน `validation/cleaned/Geographic_Data_deduplicated.csv` ซึ่ง commit ไว้แล้ว
- ผลลัพธ์ของทุกสคริปต์ commit ไว้แล้วใน `transformation/output/` จึงตรวจผลได้โดยไม่ต้องรันใหม่

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