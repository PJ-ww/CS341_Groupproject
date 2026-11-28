# คู่มือทดลองรันโปรเจกต์ CS341 Flood Impact & Recovery (เชียงใหม่)

คู่มือนี้อธิบายวิธี clone repo แล้วรันส่วน **Transformation → Integration → Storage (Parquet) → Query** บนเครื่องของตัวเอง **โดยไม่ต้องใช้ AWS Account หรือ Credentials**

ข้อมูลดิบ 5 ไฟล์**ไม่ได้อยู่ใน GitHub** (`ingestion/data/` อยู่ใน `.gitignore`) แต่ข้อมูลหลังผ่าน validation ของทั้ง 5 ไฟล์อยู่ใน `validation/cleaned/` จึงรันต่อได้ทันที และผลลัพธ์ทุกขั้นที่ทีมรันไว้ก็อยู่ใน repo (`transformation/output/`, `storage/curated/`, `storage/query_results/`) เปิดตรวจได้โดยไม่ต้องรัน ที่มาของข้อมูลแต่ละไฟล์ดูที่ [`data_catalog/sources.md`](data_catalog/sources.md)

ใช้เวลาติดตั้งและรันประมาณ 5 นาที

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

`requirements.txt` มี pandas, pyarrow, openpyxl (อ่าน `.xlsx`), duckdb (รัน SQL ในเครื่อง) และ boto3

---

## 3. รันทั้ง pipeline ด้วยคำสั่งเดียว

```bash
python run_all.py
```

ผลที่ถูกต้อง: ทุกขั้นขึ้น `[OK]` และท้ายสุดขึ้น `เสร็จสมบูรณ์: ทุกขั้นตอนผ่าน และจำนวนแถวตรงกับที่ทีมรายงานไว้`

| ตัวเลือก | ใช้เมื่อ |
|---|---|
| (ไม่มี) | เริ่มจาก `validation/cleaned/` ที่ commit ไว้ |
| `--from-raw` | มีไฟล์ดิบครบ 5 ไฟล์ใน `ingestion/data/` และต้องการรัน validation ก่อน (ดูขั้นตอนที่ 6) |
| `--verbose` | ดูข้อความที่แต่ละสคริปต์พิมพ์ออกมา |

ขั้นตอนที่ 4–5 ด้านล่างคือคำสั่งเดียวกันแบบรันทีละขั้น

---

## 4. รัน Transformation & Integration

รันตามลำดับนี้จาก root ของโปรเจกต์ (สคริปต์ `integrate_*` ใช้ผลลัพธ์ของ `transform_*`)

```bash
python transformation/scripts/transform_flood.py
python transformation/scripts/transform_damage.py
python transformation/scripts/transform_household_income.py
python transformation/scripts/transform_village_mapping.py
python transformation/scripts/integrate_flood_mapping.py
python transformation/scripts/integrate_household_income_mapping.py
```

### ผลลัพธ์ที่คาดหวัง

| ไฟล์ใน `transformation/output/` | แถว | หมายเหตุ |
|---|---:|---|
| `flood_2566_transformed.csv` | 1,198 | คัดเฉพาะเชียงใหม่จาก 19,584 แถว |
| `flood_2567_transformed.csv` | 3,556 | คัดเฉพาะเชียงใหม่จาก 34,875 แถว |
| `flood_chiangmai_combined.csv` | 4,754 | รวมสองปี |
| `chiangmai_damage_transformed.csv` | 866 | |
| `household_income_transformed.csv` | 2,154 | |
| `village_mapping_transformed.csv` | 2,184 | |
| `flood_mapping_integrated.csv` | 4,754 | จับคู่หมู่บ้านได้ 99.31% |
| `household_income_mapping_integrated.csv` | 2,154 | จับคู่แบบ unique 67.22% |

รายงาน `.json` ของแต่ละขั้นอยู่ใน `transformation/reports/` (6 ไฟล์)

---

## 5. รัน Storage (Parquet) และ Query ในเครื่อง

```bash
python storage/build_curated.py        # CSV → Parquet ใน storage/curated/ + ตรวจจำนวนแถวและ primary key
python storage/run_local_queries.py    # รัน SQL ทั้งหมดใน sql/curated/ ด้วย DuckDB
```

- `build_curated.py` ต้องขึ้น `all checks passed` ได้ตาราง `dim_village` (2,184), `fact_flood_report` (4,754), `fact_disaster_damage` (866), `fact_household_income` (2,154)
- `run_local_queries.py` เขียนผลของ data quality `dq_01`–`dq_05` และ query ตอบ Q1–Q3 (9 ไฟล์ รวม `q2_3` และ `q3_3` ที่ใช้ตรวจความน่าเชื่อถือของผล) ไว้ใน `storage/query_results/` ผลต้องตรงกับที่รันบน Athena (ภาพใน `docs/evidence/`)

> ไฟล์ผลลัพธ์ที่ทีมรันไว้แล้วมีอยู่ในโปรเจกต์ตั้งแต่ต้น การรันซ้ำจะได้ข้อมูลเหมือนเดิม (ไฟล์ Parquet อาจต่างกันที่ metadata และ `curated_build_report.json` ต่างกันที่เวลา)

---

## 6. (ไม่บังคับ) รัน Data Validation จากไฟล์ดิบ

ต้องมีไฟล์ดิบ 5 ไฟล์ใน `ingestion/data/` ก่อน วิธีหาไฟล์อยู่ใน [`ingestion/README.md`](ingestion/README.md) หัวข้อ **6B** (ไฟล์อุทกภัย 2 ไฟล์ดาวน์โหลดได้จาก ปภ. ส่วนอีก 3 ไฟล์ไม่มีลิงก์สาธารณะ ต้องขอสำเนาจากทีม)

```bash
python ingestion/inspect_files.py      # ดู encoding, หัวตาราง, จำนวนแถว
python ingestion/validate_data.py
```

ผลลัพธ์ที่คาดหวัง:

| ไฟล์ | แถว | accepted | quarantined |
|---|---:|---:|---:|
| `flood_2566.csv` | 19,607 | 19,584 | 23 |
| `flood_2567.csv` | 34,882 | 34,875 | 7 |
| `chiangmai_damage.xlsx` | 883 | 866 | 17 |
| `household_income.xlsx` | 2,167 | 2,154 | 13 |
| `village_mapping.json` | 2,198 | 2,184 | 14 |

ไฟล์ที่ถูกสร้าง:
- `validation/reports/validation_report.json` — รายงานผลตรวจ
- `validation/cleaned/*_cleaned.csv` — แถวที่ผ่านการตรวจ (input ของขั้นตอนที่ 4)
- `validation/quarantine/*_quarantine.json` — แถวที่ไม่ผ่าน พร้อมเลขแถวต้นฉบับและเหตุผล

ข้อมูลบนเว็บต้นทางอาจอัปเดตหลังวันที่ทีมดาวน์โหลด จำนวนแถวจึงอาจไม่ตรงกับตารางนี้ทุกค่า

## 7. (ไม่บังคับ) ตรวจแพ็กเกจ Lambda

```bash
python orchestration/build_package.py
```

สร้างไฟล์ `orchestration/dist/cs341_pipeline.zip` ซึ่งเป็นแพ็กเกจโค้ดสำหรับ AWS Lambda ทั้ง 7 ฟังก์ชัน ไม่ต้องใช้ AWS

---

## 8. ส่วนที่ต้องใช้ AWS (รันบนเครื่องอื่นไม่ได้)

ส่วนต่อไปนี้ใช้ AWS Account ของทีม ซึ่งไม่ได้แจก Credentials เพื่อความปลอดภัย จึงไม่จำเป็นต้องรัน ถ้าต้องการลองบน AWS Account ของตัวเอง ทำตาม [`orchestration/README.md`](orchestration/README.md) และ [`storage/README.md`](storage/README.md)

| ส่วน | ไฟล์ | หมายเหตุ |
|---|---|---|
| อัปโหลดข้อมูลดิบขึ้น S3 | `ingestion/ingest.py` | ต้องมี AWS Credentials ถ้ารันโดยไม่มีจะขึ้น error ซึ่งเป็นเรื่องปกติ |
| Orchestration | `orchestration/lambda_handlers.py`, `state_machine.asl.json` | Lambda + Step Functions: CheckBatch → ValidateBatch → TransformBatch → VerifyBatch → CurateBatch → QueryBatch |
| อัปโหลด Curated Zone | `storage/upload_to_s3.py` | `storage/curated/` → `s3://cs341-flood-recovery/curated/` |
| Glue Data Catalog + Athena | `storage/run_athena.py`, `sql/curated/` | ตาราง 4 ตาราง + view 2 ตัวใน `flood_recovery_db`, data quality และ query Q1–Q3 อ่าน SQL ได้โดยตรง |

หลักฐานการทำงานบน AWS ดูได้จาก:
- Demo Video: https://youtu.be/vEXtP3JA8TA
- แผนภาพสถาปัตยกรรม: [`docs/architecture_diagram.png`](docs/architecture_diagram.png)
- ภาพการรันจริงบน S3 / Athena: [`docs/evidence/`](docs/evidence/)
- รายละเอียดการออกแบบ: โฟลเดอร์ `docs/` และ `data_catalog/sources.md`

---

## 9. แก้ปัญหาเบื้องต้น

| อาการ | สาเหตุ / วิธีแก้ |
|---|---|
| `ModuleNotFoundError: duckdb` / `pyarrow` / `openpyxl` | ยังไม่ได้ติดตั้งตาม `requirements.txt` หรือยังไม่ได้เปิด venv (ขั้นตอนที่ 2) |
| `FileNotFoundError: ...validation/cleaned/...` | ไฟล์ใน `validation/cleaned/` หายไป ใช้ `git checkout -- validation/` เพื่อคืนไฟล์ |
| `--from-raw` แล้วขึ้นไม่พบไฟล์ใน `ingestion/data/` | ยังไม่มีไฟล์ดิบ หรือชื่อไฟล์ไม่ตรง (ขั้นตอนที่ 6) ถ้าไม่มีไฟล์ดิบให้รัน `python run_all.py` โดยไม่ใส่ `--from-raw` |
| `FileNotFoundError: ...transformation/output/...` ตอนรัน `integrate_*` หรือ `build_curated.py` | รันสคริปต์ไม่ตามลำดับ ให้รันตามขั้นตอนที่ 4–5 หรือใช้ `run_all.py` |
| ติดตั้ง pandas ไม่ได้ / เวอร์ชันไม่ตรง | ตรวจว่าใช้ Python 3.11+ (`python --version`) |
| ตัวอักษรไทยเพี้ยนใน Terminal บน Windows | ไม่กระทบการทำงาน ตั้ง `PYTHONIOENCODING=utf-8` หรือเปิดไฟล์ `.csv` ด้วย VS Code (ไฟล์เป็น UTF-8) |
