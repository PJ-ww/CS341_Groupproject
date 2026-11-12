
# การแปลงและประมวลผลข้อมูล (Data Transformation & Processing)

## 1. ภาพรวม

โมดูลนี้แปลงชุดข้อมูลต้นทางที่ผ่านการตรวจสอบ (validation) แล้ว ให้อยู่ในรูปแบบมาตรฐานที่เหมาะสำหรับการจัดเก็บข้อมูลและการวิเคราะห์ต่อไป

กระบวนการแปลงข้อมูลประกอบด้วย:
- การทำความสะอาดและปรับข้อมูลให้เป็นมาตรฐาน
- การแปลงชนิดข้อมูล
- การจัดการค่าที่หายไป (missing values)
- การสร้างฟีเจอร์ (feature engineering)
- การเตรียมข้อมูลสำหรับการรวมข้อมูล (integration) และการจัดเก็บ
- การส่งออกชุดข้อมูลที่แปลงแล้วในรูปแบบ CSV และ Parquet
- การสร้างรายงานการแปลงข้อมูล

## 2. หน้าที่ความรับผิดชอบ

- ทำความสะอาดและปรับชุดข้อมูลต้นทางให้เป็นมาตรฐาน
- แปลงคอลัมน์ให้เป็นชนิดข้อมูลที่เหมาะสม
- คงค่าที่หายไปไว้ตามความหมายของข้อมูลต้นทาง
- สร้างฟีเจอร์เพิ่มเติมเมื่อจำเป็น
- รวมชุดข้อมูลเฉพาะเมื่อยืนยันได้ว่าระดับพื้นที่ ช่วงเวลา และความละเอียดของข้อมูล (granularity) สอดคล้องกัน
- เตรียมชุดข้อมูลที่แปลงแล้วสำหรับโมดูล Data Storage

## 3. โครงสร้างไดเรกทอรี

```text
transformation/
├── scripts/
│   ├── clean_data.py
│   ├── standardize.py
│   ├── create_features.py
│   ├── transform_flood_village_stats.py
│   ├── transform_nso_income.py
│   ├── transform_disaster_budget.py
│   ├── transform_flood_affected_households.py
│   ├── transform_affected_households_summary.py
│   └── integrate_data.py
│
├── output/
│   ├── geographic_data_cleaned.csv
│   ├── geographic_data_standardized.csv
│   ├── geographic_data_features.csv
│   ├── flood_village_stats_transformed.csv
│   ├── flood_village_stats_transformed.parquet
│   ├── nso_household_income_transformed.csv
│   ├── nso_household_income_transformed.parquet
│   ├── disaster_budget_2564_transformed.csv
│   ├── disaster_budget_2564_transformed.parquet
│   ├── flood_affected_households_transformed.csv
│   ├── flood_affected_households_transformed.parquet
│   ├── affected_households_summary_transformed.csv
│   └── affected_households_summary_transformed.parquet
│
├── reports/
│   ├── geographic_data_cleaning_report.json
│   ├── geographic_data_standardization_report.json
│   ├── geographic_data_features_report.json
│   ├── flood_village_stats_transformation_report.json
│   ├── nso_household_income_transformation_report.json
│   ├── disaster_budget_2564_transformation_report.json
│   ├── flood_affected_households_transformation_report.json
│   └── affected_households_summary_transformation_report.json
│
└── README.md
```

## 4. ชุดข้อมูลนำเข้า

โมดูลนี้ใช้ชุดข้อมูลต้นทางที่ผ่านการตรวจสอบจากกระบวนการ Data Validation แล้ว

| ชุดข้อมูล | ชื่อไฟล์ที่ดาวน์โหลด (`ingestion/data/`) | ไฟล์ที่สคริปต์อ่าน (`ingestion/data/` + S3 key) | แหล่งที่มา |
|---|---|---|---|
| Geographic Data | - | `validation/cleaned/Geographic_Data_deduplicated.csv` (commit ไว้ใน Git) | ปภ. (PDPM) |
| Flood Village Stats | `STATISTIC_FLD.xlsx` | `raw/pdpm/flood_stats/pdpm_flood_village_stats.xlsx` | ปภ. (PDPM) |
| Household Income | `Salary.csv` | `raw/nso/nso_household_income.csv` | สสช. (NSO) |
| Disaster Budget | `2564_by_disaster_type1.csv` | `raw/pdpm/flood_stats/pdpm_2564_by_disaster_type.csv` | ปภ. (PDPM) |
| Flood Affected Households | `Number_of Households_Affected_by_Flooding.csv` | `raw/pdpm/flood_relief/pdpm_flood_affected_households.csv` | ปภ. (PDPM) |
| Affected Households Summary | `Number_of_Affected_Households.xlsx` | `raw/pdpm/flood_relief/pdpm_affected_households.xlsx` | ปภ. (PDPM) |

ไฟล์ดิบ (raw files) ไม่ได้จัดเก็บไว้ใน Git ให้ดาวน์โหลดไฟล์ไว้ที่ `ingestion/data/` ก่อน โดยดาวน์โหลดจาก S3 หรือจากแหล่งข้อมูลต้นฉบับ (ดู [`ingestion/README.md`](../ingestion/README.md) หัวข้อ 6 และ 6B) จากนั้นรัน `python prepare_local_data.py` ซึ่งจะคัดลอกแต่ละไฟล์ไปไว้ที่ `ingestion/data/<S3 key>` (โครงสร้างเดียวกับที่สคริปต์ `transform_*.py` และ working directory ของ Lambda ใช้) การจับคู่ชื่อไฟล์มาจาก `local_file`, `s3_prefix` และ `s3_name` ใน [`ingestion/config.py`](../ingestion/config.py)

หมายเหตุ:
- Geographic Data ใช้ผลลัพธ์ที่ลบข้อมูลซ้ำแล้ว (deduplicated) จาก Data Validation
- Flood Village Stats ใช้ไฟล์ Excel ดิบ เนื่องจากไม่มีไฟล์ผลลัพธ์ที่ผ่านการยอมรับ (accepted output) แยกไว้ในเครื่อง โดย Validation Report ระบุว่าทั้ง 57,024 แถวผ่านการยอมรับ
- ชุดข้อมูลอื่น ๆ ในตารางได้รับการยืนยันว่าผ่านการยอมรับใน Validation Report แล้ว และใช้ไฟล์ดิบเป็นข้อมูลนำเข้าเนื่องจากไม่มีไฟล์ผลลัพธ์ที่ผ่านการยอมรับแยกไว้ในเครื่อง

## 5. กระบวนการแปลงข้อมูล

### 5.1 Geographic Data

สคริปต์:
- `clean_data.py`
- `standardize.py`
- `create_features.py`

การประมวลผล:
- ลบช่องว่างที่อยู่หน้าและท้ายข้อความ
- ปรับชนิดข้อมูลและหมวดหมู่ความเสี่ยงให้เป็นมาตรฐาน
- สร้างคอลัมน์ `risk_level_code`
- สร้างคอลัมน์ `risk_level`

ผลลัพธ์:
- `geographic_data_cleaned.csv`
- `geographic_data_standardized.csv`
- `geographic_data_features.csv`

ผลการประมวลผล:
- จำนวนแถวนำเข้า: 1,772
- จำนวนแถวผลลัพธ์: 1,772
- จำนวนแถวที่ถูกลบระหว่างการแปลง: 0
- จำนวนคอลัมน์ผลลัพธ์สุดท้าย: 9

### 5.2 Flood Village Stats

สคริปต์:
- `transform_flood_village_stats.py`

การประมวลผล:
- ปรับชื่อคอลัมน์ให้เป็นมาตรฐาน
- แปลงคอลัมน์ข้อความเป็นชนิด String
- คงรหัสพื้นที่ไว้เป็นชนิด String
- แปลงคอลัมน์รายปี `Y2562–Y2567` เป็นจำนวนเต็มที่รองรับค่าว่าง (nullable integer)
- คงค่ารายปีที่หายไปไว้
- สร้างคอลัมน์ `years_with_reported_value`

ผลลัพธ์:
- `flood_village_stats_transformed.csv`
- `flood_village_stats_transformed.parquet`

ผลการประมวลผล:
- จำนวนแถวนำเข้า: 57,024
- จำนวนแถวผลลัพธ์: 57,024
- จำนวนแถวที่ถูกลบ: 0
- จำนวนคอลัมน์ผลลัพธ์: 19

### 5.3 NSO Household Income

สคริปต์:
- `transform_nso_income.py`

การประมวลผล:
- ปรับคอลัมน์ข้อความให้เป็นมาตรฐาน
- แปลง `year` เป็นจำนวนเต็มที่รองรับค่าว่าง
- แปลง `value` เป็นตัวเลข
- คงค่าศูนย์และค่าติดลบไว้
- คงค่าที่หายไปในคอลัมน์ `attribute` ไว้
- ไม่รวม (aggregate) หมวดหมู่รายได้

ผลลัพธ์:
- `nso_household_income_transformed.csv`
- `nso_household_income_transformed.parquet`

ผลการประมวลผล:
- จำนวนแถวนำเข้า: 15,400
- จำนวนแถวผลลัพธ์: 15,400
- จำนวนแถวที่ถูกลบ: 0
- จำนวนคอลัมน์ผลลัพธ์: 11

ข้อจำกัดสำคัญ:
- ข้อมูลรายได้จำแนกตามกลุ่มเศรษฐสังคมในระดับจังหวัด
- ไม่ได้แสดงรายได้ของครัวเรือนรายครัวเรือน
- จังหวัดยโสธรมี 100 ระเบียนในปี 2568 แต่ระเบียนเหล่านี้แทนหมวดหมู่รายได้และกลุ่มเศรษฐสังคมที่แตกต่างกัน

### 5.4 Disaster Budget 2564

สคริปต์:
- `transform_disaster_budget.py`

การประมวลผล:
- เลือกระเบียนระดับจังหวัดจากส่วนที่ 1 (วงเงินจังหวัด)
- ตัดแถวสรุปและระเบียนที่อยู่นอกส่วนที่ 1 ออก
- ลบเครื่องหมายจุลภาคก่อนแปลงเป็นตัวเลข
- แปลงค่าขีด (`-` และ `--`) เป็นค่าที่หายไป
- เพิ่มปีพุทธศักราช 2564
- คงข้อมูลงบประมาณระดับจังหวัดไว้

ผลลัพธ์:
- `disaster_budget_2564_transformed.csv`
- `disaster_budget_2564_transformed.parquet`

ผลการประมวลผล:
- จำนวนแถวต้นฉบับ: 83
- จำนวนแถวที่แปลงแล้ว: 76
- จำนวนจังหวัด: 76
- จำนวนแถวที่ถูกตัดออก: 7
- จำนวนคอลัมน์ผลลัพธ์: 17

ข้อจำกัดสำคัญ:
- ชุดข้อมูลนี้แสดงข้อมูลงบประมาณระดับจังหวัดของปี 2564
- ตัดกรุงเทพมหานครจากส่วนที่ 2 และระเบียนสรุปที่ไม่ใช่จังหวัดออก

### 5.5 Flood Affected Households

สคริปต์:
- `transform_flood_affected_households.py`

การประมวลผล:
- ปรับค่าข้อความให้เป็นมาตรฐาน
- แปลงปีและจำนวนครัวเรือนเป็นจำนวนเต็มที่รองรับค่าว่าง
- คงค่าศูนย์และค่าที่หายไปไว้
- ไม่รวมระเบียนข้ามพื้นที่

ผลลัพธ์:
- `flood_affected_households_transformed.csv`
- `flood_affected_households_transformed.parquet`

ผลการประมวลผล:
- จำนวนแถวนำเข้า: 144
- จำนวนแถวผลลัพธ์: 144
- จำนวนแถวที่ถูกลบ: 0
- จำนวนคอลัมน์ผลลัพธ์: 7

ข้อจำกัดสำคัญ:
- ชุดข้อมูลนี้มีระเบียนครัวเรือนที่ได้รับผลกระทบจากอุทกภัยของจังหวัดพังงา
- ซึ่งเป็นพื้นที่ต่างจาก Geographic Data ของจังหวัดยโสธร

### 5.6 Affected Households Summary

สคริปต์:
- `transform_affected_households_summary.py`

การประมวลผล:
- อ่านข้อมูลจากชีต Excel `Sheet2`
- ปรับคอลัมน์ข้อความให้เป็นมาตรฐาน
- แปลง `จำนวน` เป็นจำนวนเต็มที่รองรับค่าว่าง
- คงรอบเหตุการณ์และหน่วยวัดต้นฉบับไว้
- ไม่รวมค่าที่มีหน่วยวัดต่างกัน
- ไม่สร้างคอลัมน์ปี เนื่องจากข้อมูลต้นทางไม่ได้ระบุปีไว้

ผลลัพธ์:
- `affected_households_summary_transformed.csv`
- `affected_households_summary_transformed.parquet`

ผลการประมวลผล:
- จำนวนแถวนำเข้า: 48
- จำนวนแถวผลลัพธ์: 48
- จำนวนแถวที่ถูกลบ: 0
- จำนวนคอลัมน์ผลลัพธ์: 5

ข้อจำกัดสำคัญ:
- ชุดข้อมูลมีหน่วยวัดที่แตกต่างกัน 3 หน่วย:
  - ตำบล
  - หมู่บ้าน
  - ครัวเรือน
- ต้องตีความค่าแยกกันตามหน่วยวัดของแต่ละค่า

## 6. ข้อพิจารณาในการรวมข้อมูล (Integration)

ควรเชื่อม (join) ชุดข้อมูลเฉพาะเมื่อระดับพื้นที่ ช่วงเวลา และความละเอียดของข้อมูลสอดคล้องกันเท่านั้น

ข้อพิจารณาในปัจจุบัน:

- Geographic Data มีข้อมูลความเสี่ยงระดับตำบลและหมู่บ้านของจังหวัดยโสธร
- NSO Household Income มีข้อมูลกลุ่มเศรษฐสังคมระดับจังหวัด อาจพิจารณาความสัมพันธ์เชิงบริบทระดับจังหวัด-ปีสำหรับยโสธรในปี 2568 ได้ แต่ห้ามตีความว่าเป็นรายได้ระดับครัวเรือน
- Disaster Budget มีข้อมูลระดับจังหวัดของปี 2564 สามารถใช้วิเคราะห์ระดับจังหวัดได้เมื่อระบุข้อจำกัดด้านพื้นที่และช่วงเวลาไว้อย่างชัดเจน
- Flood Affected Households เป็นข้อมูลของจังหวัดพังงา จึงไม่ควรเชื่อมโดยตรงกับ Geographic Data ของยโสธร
- Affected Households Summary มีข้อมูลระดับอำเภอของจังหวัดหนองคายและมีหน่วยวัดหลายหน่วย ต้องยืนยันความสอดคล้องด้านปีและพื้นที่ก่อนนำไปรวม
- `pdpm_gd015.csv` ซ้ำซ้อนกับ Flood Village Stats และไม่มีค่ารายปีที่ไม่ว่างเพิ่มเติมสำหรับระเบียนที่ตรงกัน จึงไม่ใช้เป็นแหล่งข้อมูลเสริม

ได้สร้างชุดข้อมูลที่รวมแล้วหนึ่งชุด คือ `geographic_nso_integrated` (`integrate_data.py`)

- คีย์ที่ใช้เชื่อม: `จังหวัด` + `ปี` (ยโสธร, 2568) โดยกลุ่มเศรษฐสังคมของ NSO หลายกลุ่มเชื่อมกับสรุปความเสี่ยงเชิงพื้นที่หนึ่งชุด (ตรวจสอบแล้วว่าเป็นแบบ many-to-one)
- ข้อมูลนำเข้า: Geographic 1,772 แถว (เหลือ 886 แถวหลังกรองปี 2568) และ NSO 15,400 แถว (เหลือ 10 แถวหลังกรองยโสธร ปี 2568 และ `รายได้ทั้งสิ้นต่อเดือน`)
- ผลลัพธ์: 10 แถว แถวละหนึ่งกลุ่มเศรษฐสังคม โดยแต่ละแถวมีจำนวนและร้อยละของระดับความเสี่ยงชุดเดียวกัน
- รายงาน: `transformation/reports/geographic_nso_integration_report.json`

ตารางนี้เป็นตารางบริบทระดับจังหวัด-ปี ไม่ใช่ fact table ระดับครัวเรือนหรือหมู่บ้าน จึงไม่สามารถแสดงความสัมพันธ์ระหว่างรายได้กับความเสี่ยงอุทกภัยภายในจังหวัดได้ การเชื่อมข้อมูลอื่น ๆ ยังอยู่นอกขอบเขตจนกว่าระดับพื้นที่และช่วงเวลาจะสอดคล้องกัน

## 7. คุณภาพข้อมูลและข้อจำกัด

- ไม่มีการแก้ไขไฟล์ดิบต้นฉบับ
- คงค่าที่หายไปไว้เมื่อค่านั้นหมายถึงข้อมูลที่ไม่มีหรือไม่ได้รายงาน
- คงค่าศูนย์ไว้เมื่อเป็นค่าที่รายงานจริง
- ค่าขีดในชุดข้อมูลงบประมาณถือเป็นค่าที่หายไป ไม่ใช่ศูนย์
- ไม่รวมหมวดหมู่รายได้เป็นรายได้ระดับครัวเรือน
- ไม่นำค่าที่มีหน่วยวัดต่างกันมารวมกัน
- ต้องระบุความไม่สอดคล้องด้านพื้นที่และช่วงเวลาไว้ก่อนการรวมข้อมูล
- รายงานการแปลงข้อมูลบันทึกจำนวนแถว ค่าที่หายไป และรายละเอียดการแปลง

## 8. วิธีการรัน

รันคำสั่งจากไดเรกทอรีรากของ repository

### 8.1 สิ่งที่ต้องเตรียม

```bash
python -m pip install -r requirements.txt
```

ต้องใช้ Python 3.11 ขึ้นไป (pandas 3.x) และ `openpyxl` (สำหรับไฟล์ `.xlsx`) รวมอยู่ใน `requirements.txt` แล้ว

### 8.2 วิธีด่วน: คำสั่งเดียว

```bash
python run_all.py
```

`run_all.py` จะเตรียมไฟล์ดิบ รัน validation รันสคริปต์แปลงข้อมูลทุกตัวตามลำดับที่ถูกต้อง และตรวจสอบจำนวนแถวของผลลัพธ์เทียบกับค่าที่ระบุใน README นี้ โดยจะหยุดทันทีเมื่อขั้นตอนใดล้มเหลว เพิ่ม `--verbose` เพื่อดูผลลัพธ์ของแต่ละสคริปต์

### 8.3 ทีละขั้นตอน

สคริปต์แปลงข้อมูลบางตัวอ่านไฟล์ดิบจาก `ingestion/data/raw/...` (โครงสร้างเดียวกับ S3 และ working directory ของ Lambda) โดย `prepare_local_data.py` จะคัดลอกไฟล์ที่ดาวน์โหลดไว้ใน `ingestion/data/` ไปยังโครงสร้างดังกล่าว ให้รันหนึ่งครั้งก่อนรันสคริปต์แปลงข้อมูล

```bash
python prepare_local_data.py
python ingestion/validate_data.py
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

ลำดับมีความสำคัญ: `integrate_data.py` ต้องใช้ผลลัพธ์จาก `create_features.py` และ `transform_nso_income.py` ส่วน `clean_data.py` อ่านไฟล์ `validation/cleaned/Geographic_Data_deduplicated.csv` ที่สร้างโดย `validate_data.py`

ต้องใช้ `pandas`, `pyarrow` และ `openpyxl` (`python -m pip install -r requirements.txt`) สคริปต์สามตัวแรกต้องการเพียงไฟล์ใน `validation/cleaned/` ที่ commit ไว้แล้ว ส่วนสคริปต์ `transform_*.py` ต้องมีไฟล์ดิบใน `ingestion/data/raw/...` (สร้างโดย `prepare_local_data.py`)

### 8.4 พฤติกรรมเมื่อรันซ้ำ

สคริปต์จะเขียนทับผลลัพธ์เดิม การรันซ้ำจึงได้ไฟล์ CSV เหมือนเดิม ไฟล์ Parquet อาจมีไบต์ต่างกัน (metadata ของไฟล์ขึ้นกับเวอร์ชันของไลบรารีหรือสภาพแวดล้อม) แต่ข้อมูลภายในเหมือนกัน ให้เปรียบเทียบด้วย `pd.read_parquet(...).equals(...)` แทนการเทียบ checksum ส่วนรายงาน JSON จะต่างกันเฉพาะตัวคั่น path (Windows กับ macOS/Linux) และลำดับไฟล์

## 9. รูปแบบผลลัพธ์

- CSV: เหมาะสำหรับการตรวจดูข้อมูลและการแลกเปลี่ยนข้อมูล
- Parquet: เหมาะสำหรับการประมวลผลเชิงวิเคราะห์และการจัดเก็บข้อมูล
- JSON: รายงานการแปลงข้อมูลที่มีผลการประมวลผลและข้อมูลด้านคุณภาพข้อมูล

## 10. เครื่องมือ

- Python
- Pandas
- PyArrow
- Boto3 (สำหรับเชื่อมต่อ AWS S3 เมื่อจำเป็น)
