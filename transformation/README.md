# การแปลงและประมวลผลข้อมูล (Data Transformation & Processing)

## ภาพรวม (Overview)

โมดูลนี้ทำหน้าที่แปลงชุดข้อมูลที่ผ่านขั้นตอนการตรวจสอบความถูกต้องจาก Data Validation ให้อยู่ในรูปแบบที่เป็นมาตรฐานและเหมาะสมสำหรับการนำไปวิเคราะห์ต่อ โดยเน้นการปรับชนิดข้อมูล ชื่อคอลัมน์ การจัดการ Missing Values การสร้างฟิลด์ใหม่ และการส่งออกข้อมูลในรูปแบบ CSV และ Parquet

## หน้าที่รับผิดชอบ (Responsibilities)

- ทำความสะอาดชุดข้อมูลที่ผ่านการตรวจสอบแล้ว
- ปรับมาตรฐานชื่อคอลัมน์และชนิดข้อมูล
- ปรับรูปแบบข้อมูลทางภูมิศาสตร์ให้เหมาะสมกับการใช้งาน
- สร้างฟิลด์หรือคอลัมน์ใหม่จากข้อมูลเดิมเมื่อมีความจำเป็น
- รวมชุดข้อมูลเมื่อมีคีย์ที่เหมาะสมสำหรับเชื่อมโยงข้อมูล
- ส่งออกชุดข้อมูลที่ผ่านการแปลงแล้วในรูปแบบ CSV และ/หรือ Parquet

## โครงสร้างโฟลเดอร์ (Directory Structure)

```text
transformation/
├── scripts/
│   ├── clean_data.py
│   ├── standardize.py
│   ├── create_features.py
│   ├── transform_flood_village_stats.py
│   └── integrate_data.py
├── output/
│   ├── geographic_data_cleaned.csv
│   ├── geographic_data_standardized.csv
│   ├── geographic_data_features.csv
│   ├── flood_village_stats_transformed.csv
│   └── flood_village_stats_transformed.parquet
├── reports/
│   ├── geographic_data_cleaning_report.json
│   ├── geographic_data_standardization_report.json
│   ├── geographic_data_features_report.json
│   └── flood_village_stats_transformation_report.json
└── README.md
```

## ข้อมูลนำเข้า (Input)

ข้อมูลนำเข้ามาจากโมดูล Data Validation โดยใช้ชุดข้อมูลที่ผ่านการตรวจสอบตามกฎของโครงการ

ชุดข้อมูลที่ดำเนินการแล้ว:

1. **Geographic Data** — ใช้ไฟล์ `validation/cleaned/Geographic_Data_deduplicated.csv`
2. **Flood Village Stats** — ใช้ไฟล์ `ingestion/data/raw/pdpm/flood_stats/pdpm_flood_village_stats.xlsx` โดยอ้างอิงผล Validation Report ที่ระบุว่าผ่าน 57,024 แถว และไม่มีแถวถูก Quarantine เนื่องจากยังไม่มีไฟล์ Accepted แยกในเครื่อง

## ขั้นตอนการประมวลผล (Processing Steps)

### 1. Geographic Data

**Cleaning — `clean_data.py`**

- อ่านข้อมูล Geographic Data จาก Validation Output
- ตัดช่องว่างส่วนเกินในข้อความ
- ปรับชนิดข้อมูลปีและหมายเลขหมู่บ้านให้เหมาะสม
- ส่งออกข้อมูลที่ผ่านการทำความสะอาด

**Standardization — `standardize.py`**

- ปรับมาตรฐานชนิดข้อมูลและรูปแบบของข้อมูล
- จัดลำดับและกำหนดมาตรฐานหมวดหมู่ความเสี่ยง
- ตรวจสอบความสอดคล้องของรูปแบบข้อมูล

**Feature Engineering — `create_features.py`**

- สร้าง `risk_level_code` เพื่อแทนระดับความเสี่ยงด้วยตัวเลข
- สร้าง `risk_level` เพื่อแทนระดับความเสี่ยงในรูปแบบภาษาอังกฤษ

### 2. Flood Village Stats

**Transformation — `transform_flood_village_stats.py`**

- ปรับมาตรฐานชื่อคอลัมน์โดยตัดช่องว่างหัวท้าย และเก็บ Mapping ของชื่อเดิม
- ปรับคอลัมน์ข้อความให้เป็น String
- ปรับรหัสพื้นที่ให้เป็น String เพื่อรักษารูปแบบรหัส
- แปลงคอลัมน์รายปี `Y2562–Y2567` เป็น Nullable Integer (`Int64`)
- รักษาค่าว่างของข้อมูลรายปีเป็น Missing Values ไม่แทนด้วยศูนย์
- สร้าง Feature `years_with_reported_value` เพื่อแสดงจำนวนปีที่มีข้อมูลรายงานในแต่ละแถว

## ผลลัพธ์ (Output)

ผลลัพธ์ของการประมวลผลประกอบด้วย:

- ไฟล์ CSV สำหรับนำไปใช้งานและตรวจสอบข้อมูล
- ไฟล์ Parquet สำหรับจัดเก็บและประมวลผลข้อมูลอย่างมีประสิทธิภาพ
- ไฟล์ JSON Report สำหรับบันทึกผลการ Transformation

### Flood Village Stats Transformation Result

- Input rows: 57,024
- Output rows: 57,024
- Rows removed: 0
- Output columns: 19
- Year columns: Nullable Integer (`Int64`)
- Area code columns: String
- Missing yearly values: Preserved
- Feature created: `years_with_reported_value`

## วิธีการใช้งาน (How to Run)

รันคำสั่งจาก Root Directory ของ Repository

```bash
python transformation/scripts/clean_data.py
python transformation/scripts/standardize.py
python transformation/scripts/create_features.py
python transformation/scripts/transform_flood_village_stats.py
```

## เครื่องมือที่ใช้ (Tools)

- Python
- Pandas
- PyArrow
- Boto3 (สำหรับเชื่อมต่อและจัดการข้อมูลบน AWS S3)

## หมายเหตุและข้อจำกัด (Notes & Limitations)

- ไฟล์ Raw ต้นฉบับจะไม่ถูกแก้ไขโดยตรง
- ไม่แทนค่า Missing ในคอลัมน์รายปีด้วยศูนย์ เนื่องจากอาจทำให้ความหมายของข้อมูลเปลี่ยนแปลง
- ไม่ลบแถวข้อมูลที่ผ่านเข้ามาในขั้นตอน Transformation
- การใช้ Raw Excel สำหรับ Flood Village Stats เป็นข้อจำกัดชั่วคราว เนื่องจากยังไม่มี Accepted Output แยกจาก Person 2 ในเครื่อง
- การสร้าง Feature `years_with_reported_value` เป็นเพียงการนับจำนวนปีที่มีค่ารายงาน ไม่ได้หมายความว่าเป็นจำนวนปีที่เกิดน้ำท่วม
- `integrate_data.py` ยังอยู่ระหว่างการพัฒนา โดยจะกำหนดชุดข้อมูลและคีย์ที่ใช้เชื่อมโยงหลังจากตรวจสอบความเหมาะสมของข้อมูลแล้ว
