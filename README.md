# CS341 Group Project: Flood Impact & Recovery — Chiang Mai

## Architecture

![Architecture Diagram](docs/architecture_diagram.png)

ต้นฉบับแผนภาพคือ [`docs/architecture_diagram.svg`](docs/architecture_diagram.svg) (แก้ไฟล์ SVG แล้ว render เป็น PNG ใหม่ ดูข้อ 8.4)

## Demo Video

[![CS341 Demo](https://img.youtube.com/vi/vEXtP3JA8TA/maxresdefault.jpg)](https://youtu.be/vEXtP3JA8TA)

ลิงก์วิดีโอ: https://youtu.be/vEXtP3JA8TA

## 1. Project Overview
โครงการนี้ศึกษาผลกระทบจากอุทกภัยในจังหวัดเชียงใหม่ระดับหมู่บ้าน ปี 2566–2567 (ข้อมูลความเสียหาย 2563–2567) โดยรวบรวมข้อมูลรายงานอุทกภัยจาก ปภ. ข้อมูลความเสียหาย ข้อมูลพื้นฐานรายหมู่บ้าน และรายได้ครัวเรือน มาตรวจสอบ เชื่อมโยงด้วยรหัสหมู่บ้าน จัดเก็บเป็น Data Lake บน Amazon S3 และ query ด้วย Amazon Athena เพื่อตอบว่าพื้นที่ใดได้รับผลกระทบมาก ปัจจัยด้านพื้นที่ใดเกี่ยวข้อง และควรจัดลำดับความช่วยเหลืออย่างไร

## 2. Problem statement

แต่ละหมู่บ้านในเชียงใหม่ถูกรายงานว่าเกิดอุทกภัยบ่อยไม่เท่ากัน และมีลักษณะพื้นที่ (ติดแม่น้ำ ติดภูเขา) จำนวนประชากร และรายได้ครัวเรือนต่างกัน หน่วยงานที่ต้องจัดสรรความช่วยเหลือซึ่งมีจำกัดจึงต้องรู้ว่าพื้นที่ใดได้รับผลกระทบซ้ำ และพื้นที่ใดเปราะบาง แต่ข้อมูลเหล่านี้กระจายอยู่หลายไฟล์ คนละรูปแบบ คนละระดับพื้นที่ และมีค่าว่างมาก โครงการนี้จึงสร้าง pipeline ที่เชื่อมข้อมูลเหล่านี้ในระดับหมู่บ้านอย่างตรวจสอบย้อนกลับได้ และระบุให้ชัดว่าข้อมูลตอบอะไรได้และไม่ได้

## 3. Research Questions
1. **Q1:** พื้นที่ใดในจังหวัดเชียงใหม่ได้รับผลกระทบจากอุทกภัยมากที่สุด และรูปแบบผลกระทบเปลี่ยนแปลงอย่างไรในแต่ละปี?
2. **Q2:** ลักษณะทางภูมิศาสตร์และประชากรของหมู่บ้าน (ติดแม่น้ำ ติดภูเขา ประชากร รายได้ครัวเรือน) มีความสัมพันธ์กับผลกระทบจากอุทกภัยหรือไม่?
3. **Q3:** หากทรัพยากรช่วยเหลือมีจำกัด ควรจัดลำดับความสำคัญของหมู่บ้านและอำเภอที่ควรได้รับความช่วยเหลืออย่างไร?

**ทำไมเปลี่ยนจากคำถามชุดแรก (proposal):** ชุดแรกถามเรื่องปัจจัยเมื่อระดับน้ำใกล้เคียงกัน การฟื้นตัว และความช่วยเหลือ ระดับประเทศ แต่เมื่อตรวจไฟล์จริงพบว่า (1) ไม่มีข้อมูลระยะเวลาฟื้นตัวและไม่มีข้อมูลความช่วยเหลือที่เชื่อมกับพื้นที่ที่ได้รับผลกระทบได้ (2) ไม่มีข้อมูลระดับน้ำ และ (3) ข้อมูลชุดเดิมอยู่คนละจังหวัด คนละระดับพื้นที่ และปีแทบไม่ซ้อนกัน เชื่อมกันได้จริงเพียง 10 แถว ทีมจึงจำกัดขอบเขตเป็นจังหวัดเชียงใหม่ซึ่งมีข้อมูลที่ใช้รหัสหมู่บ้านร่วมกัน และปรับคำถามให้ตรงกับข้อมูล: คำถามเรื่องการฟื้นตัว (ข้อ 2 เดิม) ถูกตัดออก ข้อ 1 เดิมกลายเป็น Q2 (ปัจจัยด้านพื้นที่ เป็นความสัมพันธ์เชิงพรรณนา) ข้อ 3 เดิมกลายเป็น Q3 (ระดับหมู่บ้าน/อำเภอ) และเพิ่ม Q1 เป็นฐานของการวิเคราะห์ รายละเอียดใน [`docs/01-problem-and-systems-thinking.md`](docs/01-problem-and-systems-thinking.md)

## 4. Data Sources

ข้อมูลดิบ 5 ไฟล์ รายละเอียดที่มา ช่วงเวลา คอลัมน์ และข้อจำกัดอยู่ใน [`data_catalog/sources.md`](data_catalog/sources.md)

| ไฟล์ | เนื้อหา | ที่มา | ช่วงเวลา |
|---|---|---|---|
| `flood_2566.csv` | รายงานเหตุการณ์อุทกภัยรายหมู่บ้าน (69 จังหวัด, คัดเฉพาะเชียงใหม่) | ปภ. [`dpm-gd027` สถิติรายปีการเกิดอุทกภัย ปี 2566](https://catalog.disaster.go.th/dataset/dpm-gd027/resource/af2370d1-d2d0-4844-a16d-e6af34926e71) | ม.ค.–ธ.ค. 2566 |
| `flood_2567.csv` | รายงานเหตุการณ์อุทกภัยรายหมู่บ้าน (72 จังหวัด, คัดเฉพาะเชียงใหม่) | ปภ. [`dpm-gd027` ปี 2567](https://catalog.disaster.go.th/dataset/dpm-gd027/resource/dde2eddc-28f5-40bf-8a62-28bc68f02af8) | ม.ค.–ธ.ค. 2567 |
| `chiangmai_damage.xlsx` | ผู้ได้รับผลกระทบและความเสียหาย เชียงใหม่ | ไฟล์ที่ทีมได้รับโดยตรง ไม่มีลิงก์สาธารณะ | 2563–2567 |
| `household_income.xlsx` | รายได้ครัวเรือนเฉลี่ยรายหมู่บ้าน (บาท/ปี) เชียงใหม่ | ไฟล์ที่ทีมได้รับโดยตรง ไม่มีลิงก์สาธารณะ | ไม่ระบุปี |
| `village_mapping.json` | ข้อมูลพื้นฐานรายหมู่บ้าน: รหัส พิกัด ประชากร ลักษณะภูมิศาสตร์ เชียงใหม่ | ไฟล์ที่ทีมได้รับโดยตรง ไม่มีลิงก์สาธารณะ | ไม่ระบุปี |

ข้อมูลดิบไม่ได้อยู่ใน Git แต่ข้อมูลหลังผ่าน validation ของทั้ง 5 ไฟล์อยู่ใน `validation/cleaned/` จึงรัน pipeline ต่อได้โดยไม่ต้องมีไฟล์ดิบ วิธีหาไฟล์ดิบดู [`ingestion/README.md`](ingestion/README.md) หัวข้อ 6B

## 5. Data Architecture
ระบบมีขั้นตอนการทำงานหลักดังนี้ (ตามแผนภาพด้านบน)

1. **Ingestion:** `ingestion/ingest.py` อัปโหลดไฟล์ดิบ 5 ไฟล์ขึ้น `s3://cs341-flood-recovery/raw/` พร้อม manifest (md5, ที่มา, ช่วงเวลา)
2. **Orchestration:** AWS Step Functions เรียก Lambda ตามลำดับ `CheckBatch` → `ValidateBatch` → `TransformBatch` → `VerifyBatch` (batch ที่ไม่ผ่านไป `QuarantineBatch`) log อยู่ใน CloudWatch
3. **Validation:** ตรวจ schema ชนิดข้อมูล ค่าว่าง แถวซ้ำ และค่าผิดรูปแบบ → `validation/cleaned/`, `validation/quarantine/`
4. **Transformation & Integration:** สคริปต์ 6 ไฟล์ คัดเฉพาะเชียงใหม่ แปลงชนิดข้อมูล และเชื่อม flood/income กับ village mapping → `transformation/output/`
5. **Storage (Curated Zone):** `storage/build_curated.py` แปลงเป็น Parquet แบบ star schema (1 dim + 3 fact) แบ่ง partition ตาม `source_year` แล้วอัปโหลดไป `s3://…/curated/`
6. **Catalog & Serving:** ลงทะเบียนตาราง 4 ตาราง + view 2 ตัวใน Glue Data Catalog (`flood_recovery_db`) แล้ว query ด้วย Athena: data quality `dq_01`–`dq_05` และคำตอบ Q1–Q3 (7 query)
7. **Results:** ผล query ใน `storage/query_results/` และภาพหลักฐานจาก Athena ใน `docs/evidence/`

ขั้น 5–6 ยังรันด้วยมือหลัง batch สำเร็จ ยังไม่ได้เป็น state ใน Step Functions

## 6. Limitations
- ไม่มีข้อมูลการฟื้นตัวและข้อมูลความช่วยเหลือที่ได้รับ จึงไม่ได้ตอบคำถามเรื่องการฟื้นตัว
- ข้อมูลอุทกภัยมีตัวเลขผู้ได้รับผลกระทบน้อย จึงใช้ "จำนวนหมู่บ้านที่ถูกรายงาน" เป็นตัวชี้วัดหลัก ซึ่งสะท้อนการรายงาน ไม่ใช่ความรุนแรงจริง
- ข้อมูลความเสียหายเชื่อมได้แค่ระดับอำเภอ รายได้และข้อมูลหมู่บ้านไม่มีปี
- ที่มาของไฟล์ `chiangmai_damage.xlsx`, `household_income.xlsx`, `village_mapping.json` ยังไม่มีลิงก์สาธารณะ
- ผลเป็นของจังหวัดเชียงใหม่ และเป็นความสัมพันธ์เชิงพรรณนา ไม่ใช่เหตุและผล (รายละเอียดในข้อ 9)


## 7. Team Members

| ชื่อสมาชิก | รหัสนักศึกษา |
|---|---|
| นางสาวณัชชา กาญจนาภา | 6709650011 |
| นายวิรภัทร สิงห์เปี้ย | 6709650094 |
| นางสาวชนิภรณ์ คิมประเสริฐ | 6709650243 |
| นางสาวพาขวัญ จุลโยธิน | 6709650532 |
| นายภัทรดร ชีวชูเกียรติ | 6709650557 |

## 8. How to Run

ขอบเขตปัจจุบัน: น้ำท่วมจังหวัดเชียงใหม่ ปี 2566–2567 (ข้อมูลความเสียหาย 2563–2567)

### 8.1 รันบนเครื่อง (ไม่ต้องใช้ AWS)

ต้องใช้ Python 3.11 ขึ้นไป ข้อมูลที่ผ่าน validation แล้วอยู่ใน `validation/cleaned/` (commit ไว้แล้ว) จึงเริ่มจากขั้น Transformation ได้ทันที

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# Transformation + Integration (คนที่ 3)
python transformation/scripts/transform_flood.py
python transformation/scripts/transform_damage.py
python transformation/scripts/transform_household_income.py
python transformation/scripts/transform_village_mapping.py
python transformation/scripts/integrate_flood_mapping.py
python transformation/scripts/integrate_household_income_mapping.py

# Storage + Query (คนที่ 4)
python storage/build_curated.py        # CSV → Parquet แบ่ง partition + ตรวจจำนวนแถว/primary key
python storage/run_local_queries.py    # รัน SQL ทั้งหมดใน sql/curated/ ด้วย DuckDB
```

`build_curated.py` ต้องขึ้น `all checks passed` ผลลัพธ์ query อยู่ใน `storage/query_results/` ผลลัพธ์ทุกขั้น commit ไว้แล้ว (`transformation/output/`, `storage/curated/`, `storage/query_results/`) จึงเปิดดูได้โดยไม่ต้องรันใหม่

> **ทางลัด:** `python run_all.py` รันคำสั่งทั้งหมดด้านบนตามลำดับในคำสั่งเดียว แล้วตรวจจำนวนแถวของผลลัพธ์ให้อัตโนมัติ (ใช้ `--from-raw` ถ้าต้องการรัน validation จากไฟล์ดิบใน `ingestion/data/` ก่อน และ `--verbose` เพื่อดูข้อความของแต่ละสคริปต์)

### 8.2 รันบน AWS (S3 + Athena)

ต้องใช้ AWS Credentials ดูวิธีตั้งค่าใน [`ingestion/README.md`](ingestion/README.md)

```bash
python storage/upload_to_s3.py                                              # → s3://cs341-flood-recovery/curated/
python storage/run_athena.py --sql sql/curated/01_create_curated_tables.sql # ตาราง 4 ตารางใน Glue Data Catalog
python storage/run_athena.py --sql sql/curated/02_create_views.sql          # view 2 ตัว
python storage/run_athena.py --sql sql/curated/data_quality --sql sql/curated/queries --save
```

หรือเปิด Athena Query Editor แล้วรันทีละ statement จากไฟล์เดียวกัน (database `flood_recovery_db`) ภาพหลักฐานการรันจริงอยู่ใน [`docs/evidence/`](docs/evidence/)

### 8.3 รายละเอียดแต่ละขั้น

| ขั้น | ทำอะไร | คู่มือ |
|---|---|---|
| 1 | สร้าง venv และติดตั้ง `python -m pip install -r requirements.txt` | [`ingestion/README.md`](ingestion/README.md) หัวข้อ 3 |
| 2 | Ingestion: นำข้อมูลดิบขึ้น S3 (`raw/`) | [`ingestion/README.md`](ingestion/README.md) |
| 3 | Validation: `python ingestion/validate_data.py` → `validation/cleaned/`, `validation/quarantine/` | [`docs/04-data-validation.md`](docs/04-data-validation.md) |
| 4 | Transformation + Integration: สคริปต์ 6 ไฟล์ตามข้อ 8.1 → `transformation/output/` | [`transformation/README.md`](transformation/README.md) |
| 5 | Storage: `python storage/build_curated.py` → Parquet ใน `storage/curated/` แล้ว `upload_to_s3.py` → `s3://cs341-flood-recovery/curated/` | [`storage/README.md`](storage/README.md) |
| 6 | Catalog + Query: สร้างตาราง/view และรัน data quality + query ตอบ Q1–Q3 จาก `sql/curated/` บน Athena | [`docs/06-storage-data-model-query.md`](docs/06-storage-data-model-query.md) |

### 8.4 แก้แผนภาพสถาปัตยกรรม

แก้ [`docs/architecture_diagram.svg`](docs/architecture_diagram.svg) แล้ว render เป็น PNG ด้วยเบราว์เซอร์ headless (Chrome หรือ Edge) จาก root ของ repo:

```bash
chrome --headless=new --hide-scrollbars --force-device-scale-factor=2 --window-size=1240,790   --screenshot=docs/architecture_diagram.png docs/architecture_diagram.svg
```

ปัญหาที่พบระหว่างทำและเหตุผลของการตัดสินใจสำคัญ สรุปไว้ใน [`docs/05-problems-and-decisions.md`](docs/05-problems-and-decisions.md) และ [`docs/06-storage-data-model-query.md`](docs/06-storage-data-model-query.md) หัวข้อ 3

## 9. สิ่งที่ต้องทำต่อก่อน Final

**ด้านการวิเคราะห์**
1. ทีมตกลงน้ำหนักคะแนนจัดลำดับพื้นที่ช่วยเหลือใน `q3_1` (ตอนนี้ใช้ ความถี่น้ำท่วม 0.5 / จำนวนครัวเรือน 0.3 / รายได้ต่ำ 0.2) และระบุเหตุผลในรายงาน
2. ทีมยืนยันการตีความผล Q1–Q3 จาก `storage/query_results/` (ผลไหนตอบคำถามได้แค่ไหน)
3. เตรียมกราฟ/ตารางและเดโมสำหรับนำเสนอ

**ด้านข้อมูล**
1. ยืนยันหน่วยงานเจ้าของข้อมูลและลิงก์ (ถ้ามี) ของ `chiangmai_damage.xlsx`, `household_income.xlsx`, `village_mapping.json` แล้วแก้ `source` / `source_url` ใน `ingestion/config.py` และ `data_catalog/sources.md` หัวข้อ 3 (ตอนนี้ระบุว่าเป็นไฟล์ที่ทีมได้รับโดยตรง ไม่มีลิงก์สาธารณะ)

**ด้าน pipeline**
1. Lambda และ Step Functions รันชุดเชียงใหม่ครบถึง `transformation/` แล้ว แต่ขั้น `storage/build_curated.py` + `upload_to_s3.py` และการรัน query บน Athena ยังรันด้วยมือ ควรเพิ่มเป็น state ต่อจาก `VerifyBatch`
2. Step Functions ยังต้องกดรันเอง ยังไม่มี trigger อัตโนมัติ (ต่อยอดด้วย EventBridge)
3. ไฟล์บน S3 ถูกเขียนทับทุกรอบ ไม่เก็บประวัติแต่ละ batch (ทางเลือก: Iceberg snapshot ใน `sql/curated/03_iceberg_optional.sql`)
4. ลบตารางขอบเขตเดิมใน Athena (`geographic`, `flood_village_stats`, `nso_income`, `nso_income_partitioned`, `disaster_budget`, `flood_affected_households`, `affected_households_summary`, `geographic_nso_integrated`) และโฟลเดอร์ `processed/` บน S3 ถ้ายังมีอยู่

**ข้อจำกัดของข้อมูลที่แก้ไม่ได้ในโครงงานนี้** (ต้องระบุในรายงาน Final)
- ไม่มีข้อมูลระยะเวลาฟื้นตัว จึงตอบไม่ได้โดยตรงว่าความช่วยเหลือทำให้ฟื้นตัวเร็วขึ้นหรือไม่
- ข้อมูลน้ำท่วมรายหมู่บ้านมี `affected_households` แค่ 15.9% (2566) และ 6.1% (2567) ของแถว จึงใช้จำนวนหมู่บ้านที่ถูกรายงานเป็นตัวชี้วัดหลัก ซึ่งสะท้อน "การถูกรายงาน" ไม่ใช่ความรุนแรงจริง และปี 2566 อาจรายงานไม่ครบเท่าปี 2567
- ข้อมูลความเสียหายปี 2567 มี 29.7% ของแถวที่ตัวเลขเป็น 0 ทุกช่อง และ `partially_damaged_houses` ปี 2566–2567 ว่างทั้งหมด จึงไม่ควรสรุปว่าความเสียหายลดลง
- ข้อมูลความเสียหายเชื่อมกับหมู่บ้านได้แค่ระดับอำเภอ เพราะ `subdistrict_id` / `village_id` ไม่ใช่รหัสมาตรฐาน
- ข้อมูลรายได้ครัวเรือนไม่มีปีกำกับ และจับคู่กับหมู่บ้านได้แบบ unique 67.22% (ambiguous 28 แถว, unmatched 678 แถว)
- ผล Q2 เป็นความสัมพันธ์เชิงพรรณนา ไม่ใช่เหตุและผล

## 10. Repository
- **GitHub Repository:** https://github.com/PJ-ww/CS341_Groupproject
- **GitHub Issues:** https://github.com/PJ-ww/CS341_Groupproject/issues
