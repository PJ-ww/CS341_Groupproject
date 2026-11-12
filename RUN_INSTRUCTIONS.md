# คู่มือทดลองรันโปรเจกต์ CS341 Flood Impact & Recovery

คู่มือนี้อธิบายวิธี clone repo แล้วรันส่วน **Validation → Transformation → Integration** บนเครื่องของตัวเอง **โดยไม่ต้องใช้ AWS Account หรือ Credentials**

ข้อมูลดิบ 8 ไฟล์**ไม่ได้อยู่ใน GitHub** (`ingestion/data/` อยู่ใน `.gitignore`) ต้องดาวน์โหลดจากเว็บต้นทางก่อน ตามขั้นตอนที่ 3 แต่ผลลัพธ์ที่ทีมรันไว้แล้วทั้งหมดอยู่ใน repo (`validation/`, `transformation/output/`, `transformation/reports/`) จึงเปิดตรวจได้ทันทีโดยไม่ต้องรัน

ใช้เวลาติดตั้งและรันประมาณ 5 นาที ไม่รวมเวลาดาวน์โหลดข้อมูลดิบ

---

## 1. สิ่งที่ต้องมี

| รายการ | รายละเอียด |
|---|---|
| Python | **3.11 ขึ้นไป** (ทีมพัฒนาด้วย pandas 3.x ซึ่งต้องใช้ Python 3.11+) |
| ระบบปฏิบัติการ | macOS / Linux / Windows |
| อินเทอร์เน็ต | ใช้เฉพาะตอนติดตั้งไลบรารี |

---

## 2. ติดตั้ง

Clone repo แล้วเปิด Terminal (Windows: PowerShell) ที่โฟลเดอร์ `CS341_Groupproject`

```bash
git clone https://github.com/PJ-ww/CS341_Groupproject.git
cd CS341_Groupproject
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

- `requirements.txt` มีครบทั้ง pandas, pyarrow, openpyxl (อ่าน `.xlsx`) และ boto3
- หากติดตั้งเวอร์ชันที่ระบุใน `requirements.txt` ไม่ได้ ให้ใช้คำสั่งนี้แทน:
  ```bash
  python -m pip install pandas pyarrow openpyxl
  ```

---

## 3. เตรียมไฟล์ข้อมูลดิบ (ทำครั้งเดียว)

**3.1 ดาวน์โหลดข้อมูลดิบ 8 ไฟล์**

ดาวน์โหลดจากหน้าชุดข้อมูลต้นทาง แล้วเปลี่ยนชื่อและวางไว้ใน `ingestion/data/` ตามตารางใน [`ingestion/README.md`](ingestion/README.md) หัวข้อ **6B** (สมาชิกทีมที่มี AWS Credentials ใช้หัวข้อ 6 โหลดจาก S3 แทนได้)

ถ้ายังไม่มีข้อมูลดิบ ยังรันได้บางส่วน:
- `clean_data.py` → `standardize.py` → `create_features.py` รันได้เลย เพราะใช้ `validation/cleaned/Geographic_Data_deduplicated.csv` ที่อยู่ใน repo
- ขั้นอื่นต้องมีข้อมูลดิบ ถ้าไม่มีจะขึ้น `[MISSING]` ในขั้น 3.2 และ `run_all.py` จะหยุดที่ขั้นแรก

ข้อมูลบนเว็บต้นทางอาจอัปเดตหลังวันที่ทีมดาวน์โหลด (6 พ.ย. 2569) จำนวนแถวจึงอาจไม่ตรงกับตารางด้านล่างทุกค่า

**3.2 จัดโครงสร้างโฟลเดอร์**

สคริปต์ transformation 5 ตัวอ่านไฟล์จากโฟลเดอร์ `ingestion/data/raw/...` ซึ่งเลียนแบบโครงสร้างบน S3 ให้รันสคริปต์ช่วยที่อยู่ที่ root ของ repo:

```bash
python prepare_local_data.py
```

ผลลัพธ์ที่ถูกต้อง: ขึ้น `[OK] ...` ครบ 8 บรรทัด และไม่มี `[MISSING]`

---

> **ทางลัด:** หลังติดตั้งและวางไฟล์ดิบเสร็จ รัน `python run_all.py` คำสั่งเดียวแทนขั้นตอนที่ 3–5 ได้ (ใช้ `--verbose` เพื่อดูข้อความของแต่ละสคริปต์) ท้ายสุดจะตรวจจำนวนแถวของผลลัพธ์ให้อัตโนมัติ ส่วนขั้นตอนด้านล่างเป็นการรันทีละขั้นเพื่อดูผลลัพธ์แต่ละส่วน

## 4. รัน Data Validation

```bash
python ingestion/validate_data.py
```

ผลลัพธ์ที่คาดหวัง (จำนวนแถวที่ผ่าน/ถูกกักกัน):

| ไฟล์ | accepted | quarantined |
|---|---:|---:|
| 2564_by_disaster_type1.csv | 76 | 7 |
| Geographic_Data.csv | 1,772 | 44 |
| Number_of Households_Affected_by_Flooding.csv | 144 | 0 |
| Number_of_Affected_Households.xlsx | 48 | 0 |
| STATISTIC_FLD.xlsx | 57,024 | 0 |
| Salary.csv | 15,400 | 0 |
| Salary2.csv | 144 | 0 |
| dpm-gd015__1.csv | 29,999 | 0 |

ไฟล์ที่ถูกสร้าง:
- `validation/reports/validation_report.json` — รายงานผลตรวจ
- `validation/cleaned/Geographic_Data_deduplicated.csv` — ข้อมูลภูมิศาสตร์ที่ตัดข้อมูลซ้ำแล้ว (ใช้เป็น input ของขั้นถัดไป)
- `validation/quarantine/*.jsonl` — แถวที่ไม่ผ่านการตรวจ

---

## 5. รัน Transformation & Integration

รันตามลำดับนี้จาก root ของโปรเจกต์ (ลำดับสำคัญ เพราะบางสคริปต์ใช้ผลลัพธ์ของสคริปต์ก่อนหน้า)

```bash
python transformation/scripts/clean_data.py
python transformation/scripts/standardize.py
python transformation/scripts/create_features.py
python transformation/scripts/transform_flood_village_stats.py
python transformation/scripts/transform_nso_income.py
python transformation/scripts/transform_disaster_budget.py
python transformation/scripts/transform_flood_affected_households.py
python transformation/scripts/transform_affected_households_summary.py
python transformation/scripts/integrate_data.py
```

> `integrate_data.py` ต้องรันหลัง `create_features.py` และ `transform_nso_income.py` เสมอ

### ผลลัพธ์ที่คาดหวัง

| ชุดข้อมูล | แถว input | แถว output |
|---|---:|---:|
| Geographic Data (3 ขั้นตอน) | 1,772 | 1,772 |
| Flood Village Stats | 57,024 | 57,024 |
| NSO Household Income | 15,400 | 15,400 |
| Disaster Budget 2564 | 83 | 76 (ตัด 7 แถวสรุป) |
| Flood Affected Households | 144 | 144 |
| Affected Households Summary | 48 | 48 |
| Geographic + NSO Integrated | 1,772 / 15,400 | 10 |

ไฟล์ที่ถูกสร้าง:
- `transformation/output/` — ไฟล์ผลลัพธ์ `.csv` และ `.parquet` (รวม 15 ไฟล์)
- `transformation/reports/` — รายงาน `.json` ของแต่ละขั้นตอน (รวม 9 ไฟล์)

> ไฟล์ผลลัพธ์ที่ทีมรันไว้แล้วมีอยู่ในโปรเจกต์ตั้งแต่ต้น การรันซ้ำจะเขียนทับไฟล์เดิมด้วยผลลัพธ์ที่เหมือนกัน

ตรวจสอบเร็ว ๆ ด้วย Python:

```bash
python -c "import pandas as pd; print(len(pd.read_parquet('transformation/output/flood_village_stats_transformed.parquet')))"
```

ควรได้ `57024`

---

## 6. (ไม่บังคับ) ตรวจดูข้อมูลดิบ

```bash
python ingestion/inspect_files.py
```

แสดง encoding, จำนวนแถว และตัวอย่างหัวตารางของไฟล์ใน `ingestion/data/`

## 7. (ไม่บังคับ) ตรวจแพ็กเกจ Lambda

```bash
python orchestration/build_package.py
```

สร้างไฟล์ `orchestration/dist/cs341_pipeline.zip` (ประมาณ 25 KB) ซึ่งเป็นแพ็กเกจโค้ดสำหรับ AWS Lambda ทั้ง 5 ฟังก์ชัน ไม่ต้องใช้ AWS

---

## 8. ส่วนที่ต้องใช้ AWS (รันบนเครื่องอื่นไม่ได้)

ส่วนต่อไปนี้ใช้ AWS Account ของทีม ซึ่งไม่ได้แจก Credentials เพื่อความปลอดภัย จึงไม่จำเป็นต้องรัน ถ้าต้องการลองบน AWS Account ของตัวเอง ทำตาม [`orchestration/README.md`](orchestration/README.md) (สร้าง bucket, ตาราง Athena จาก `sql/setup/01_create_tables.sql`, Lambda และ Step Functions)

| ส่วน | ไฟล์ | หมายเหตุ |
|---|---|---|
| อัปโหลดข้อมูลขึ้น S3 | `ingestion/ingest.py` | ต้องมี AWS Credentials; ถ้ารันโดยไม่มี จะขึ้น error ซึ่งเป็นเรื่องปกติ |
| Orchestration | `orchestration/lambda_handlers.py`, `state_machine.asl.json` | ทำงานบน AWS Lambda และ Step Functions |
| Query ด้วย Athena | `sql/analysis/*.sql`, `sql/data_quality/*.sql` | ต้องรันบน Athena (database `flood_recovery_db`); อาจารย์อ่านโค้ด SQL ได้โดยตรง |

หลักฐานการทำงานบน AWS ดูได้จาก:
- Demo Video: https://youtu.be/vEXtP3JA8TA
- แผนภาพสถาปัตยกรรม: `architechture/architecture_diagram.png`
- รายละเอียดการออกแบบ: โฟลเดอร์ `docs/` และ `data_catalog/sources.md`

---

## 9. แก้ปัญหาเบื้องต้น

| อาการ | สาเหตุ / วิธีแก้ |
|---|---|
| `ModuleNotFoundError: openpyxl` | ยังไม่ได้ติดตั้ง รัน `python -m pip install openpyxl` |
| `ModuleNotFoundError: pyarrow` | รัน `python -m pip install pyarrow` |
| `[MISSING] ...ingestion/data/...` | ยังไม่ได้ดาวน์โหลดไฟล์ดิบ หรือชื่อไฟล์ไม่ตรง (ขั้นตอนที่ 3.1) |
| `FileNotFoundError: ...ingestion/data/raw/...` | ยังไม่ได้รัน `python prepare_local_data.py` (ขั้นตอนที่ 3.2) |
| `FileNotFoundError: ...validation/cleaned/Geographic_Data_deduplicated.csv` | ยังไม่ได้รัน `ingestion/validate_data.py` (ขั้นตอนที่ 4) |
| `FileNotFoundError: ...nso_household_income_transformed.csv` | รัน `integrate_data.py` ก่อน `transform_nso_income.py` ให้รันสคริปต์ตามลำดับในขั้นตอนที่ 5 |
| ติดตั้ง pandas ไม่ได้ / เวอร์ชันไม่ตรง | ตรวจว่าใช้ Python 3.11+ (`python --version`) หรือใช้คำสั่งติดตั้งแบบไม่ระบุเวอร์ชัน |
| ตัวอักษรไทยเพี้ยนใน Terminal บน Windows | ไม่กระทบการทำงาน; เปิดไฟล์ `.csv` ด้วย Excel หรือ VS Code (ไฟล์เป็น UTF-8 with BOM) |
