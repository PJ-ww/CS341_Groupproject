# CS341 Group Project: Flood Impact & Recovery

## Architecture

![Architecture Diagram](docs/architecture_diagram.png)

## Demo Video

[![CS341 Demo](https://img.youtube.com/vi/vEXtP3JA8TA/maxresdefault.jpg)](https://youtu.be/vEXtP3JA8TA)

ลิงก์วิดีโอ: https://youtu.be/vEXtP3JA8TA
## 1. Project Overview
โครงการนี้ศึกษาผลกระทบจากน้ำท่วมและปัจจัยที่เกี่ยวข้องกับความเสียหายและการฟื้นตัวของผู้ประสบภัยในประเทศไทย โดยใช้ข้อมูลจริงจากหน่วยงานภาครัฐ เพื่อนำมารวบรวม ตรวจสอบ เชื่อมโยง และวิเคราะห์ข้อมูลสำหรับตอบคำถามวิจัย

## 2. Problem statement

ครัวเรือนและพื้นที่ที่เผชิญอุทกภัยอาจได้รับความเสียหายแตกต่างกัน แม้จะเผชิญระดับน้ำท่วมใกล้เคียงกัน เนื่องจากมีความแตกต่างด้านลักษณะพื้นที่ ทรัพยากรของครัวเรือน และการเข้าถึงความช่วยเหลือ โดยปัจจุบันข้อมูลจากแต่ละหน่วยงานอาจมีรูปแบบและระดับพื้นที่แตกต่างกัน อีกทั้งอาจไม่มีข้อมูลระยะเวลาฟื้นตัวของแต่ละครัวเรือนโดยตรง โครงการนี้จึงมุ่งศึกษาว่าข้อมูลจริงที่เข้าถึงได้สามารถนำมาเชื่อมโยงและใช้ตรวจสอบความสัมพันธ์ระหว่างผลกระทบจากน้ำท่วม ปัจจัยระดับพื้นที่ และการให้ความช่วยเหลือได้อย่างไร

## 3. Research Questions
1. เมื่อระดับน้ำท่วมใกล้เคียงกัน ปัจจัยใดบ้างที่อาจทำให้แต่ละพื้นที่ได้รับความเสียหายแตกต่างกัน?
2. ปัจจัยใดเกี่ยวข้องกับการฟื้นตัวจากน้ำท่วม และการได้รับความช่วยเหลือมีความสัมพันธ์กับการฟื้นตัวเร็วขึ้นหรือไม่?
3. หากมีทรัพยากรช่วยเหลือจำกัด ควรให้ความสำคัญกับพื้นที่หรือครัวเรือนกลุ่มใดก่อน?

## 4. Data Sources
- **สถิติอุทกภัยรายหมู่บ้าน:** [กรมป้องกันและบรรเทาสาธารณภัย](https://data.go.th/dataset/gdpublish-dfs_21_02)
- **ข้อมูลรายได้:** [สำนักงานสถิติแห่งชาติ](https://data.go.th/en/dataset/ns_08_20241)
- **ข้อมูลการช่วยเหลือผู้ประสบอุทกภัย:** [data.go.th](https://data.go.th/th/dataset/disaster_00013)
- **ข้อมูลจำนวนครัวเรือนที่ได้รับเงินเยียวยา:** [data.go.th](https://data.go.th/th/dataset/flood01_30)

ทีมจะตรวจสอบรายละเอียดและความพร้อมของข้อมูลจริงก่อนนำมาใช้วิเคราะห์และเชื่อมโยงกัน

## 5. Data Architecture
ระบบมีขั้นตอนการทำงานหลักดังนี้

1. **Data Sources:** รวบรวมข้อมูลจากหน่วยงานภาครัฐ
2. **Ingestion:** นำเข้าข้อมูลจากแหล่งต่าง ๆ
3. **Validation:** ตรวจสอบความถูกต้องและความครบถ้วนของข้อมูล
4. **Storage:** จัดเก็บข้อมูลบน Amazon S3
5. **Transformation & Integration:** ทำความสะอาด แปลง และเชื่อมโยงข้อมูล
6. **Query & Analysis:** ใช้ Amazon Athena สืบค้นและวิเคราะห์ข้อมูลด้วย SQL
7. **Results:** นำเสนอผลการวิเคราะห์ด้วยตารางหรือกราฟ


## 6. Limitations
ข้อมูลแต่ละแหล่งอาจมีระดับพื้นที่และช่วงเวลาที่แตกต่างกัน ข้อมูลรายได้อาจไม่ละเอียดถึงระดับครัวเรือน และอาจไม่มีข้อมูลระยะเวลาฟื้นตัวโดยตรง ดังนั้น ผลการวิเคราะห์จะขึ้นอยู่กับความครบถ้วนและความสามารถในการเชื่อมโยงข้อมูลจริง

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

ปัญหาที่พบระหว่างทำและเหตุผลของการตัดสินใจสำคัญ สรุปไว้ใน [`docs/05-problems-and-decisions.md`](docs/05-problems-and-decisions.md) และ [`docs/06-storage-data-model-query.md`](docs/06-storage-data-model-query.md) หัวข้อ 3

## 9. สิ่งที่ต้องทำต่อก่อน Final

**ด้านการวิเคราะห์**
1. ทีมตกลงน้ำหนักคะแนนจัดลำดับพื้นที่ช่วยเหลือใน `q3_1` (ตอนนี้ใช้ ความถี่น้ำท่วม 0.5 / จำนวนครัวเรือน 0.3 / รายได้ต่ำ 0.2) และระบุเหตุผลในรายงาน
2. ทีมยืนยันการตีความผล Q1–Q3 จาก `storage/query_results/` (ผลไหนตอบคำถามได้แค่ไหน)
3. เตรียมกราฟ/ตารางและเดโมสำหรับนำเสนอ

**ด้าน pipeline**
1. อัปเดต `orchestration/lambda_handlers.py` ให้เรียกสคริปต์ transformation ชุดใหม่ และเพิ่มขั้น `storage/build_curated.py` + อัปโหลด `curated/` (ตอนนี้ยังใช้ชุดขอบเขตเดิม ส่วน `run_all.py` อัปเดตแล้ว)
2. Step Functions ยังต้องกดรันเอง ยังไม่มี trigger อัตโนมัติ (ต่อยอดด้วย EventBridge)
3. จำนวนแถวที่ `VerifyBatch` ใช้เทียบใส่ตายตัวไว้ในโค้ด (`DATASETS` ใน `orchestration/lambda_handlers.py`) ต้องแก้ให้ตรงกับตารางชุดใหม่
4. ไฟล์บน S3 ถูกเขียนทับทุกรอบ ไม่เก็บประวัติแต่ละ batch (ทางเลือก: Iceberg snapshot ใน `sql/curated/03_iceberg_optional.sql`)
5. หลังแก้ข้อ 1 แล้ว ลบตารางขอบเขตเดิมใน Athena (`geographic`, `flood_village_stats`, `nso_income`, `nso_income_partitioned`, `disaster_budget`, `flood_affected_households`, `affected_households_summary`, `geographic_nso_integrated`) และโฟลเดอร์ `processed/` บน S3

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
