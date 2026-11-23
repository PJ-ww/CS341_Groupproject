# Transformation & Data Integration
## CS341 Term Project — Flood Impact and Recovery in Chiang Mai

**Scope:** Data Transformation, Data Quality Checks, and Data Integration

---

# 1. Overview

โฟลเดอร์นี้จัดเก็บกระบวนการ Transformation และ Integration สำหรับโครงงาน CS341 Term Project ซึ่งศึกษาผลกระทบจากอุทกภัยและแนวทางการฟื้นฟูในจังหวัดเชียงใหม่

หน้าที่หลักของส่วน Transformation คือการนำข้อมูลที่ผ่านกระบวนการ Cleaning และ Validation มาแปลงให้อยู่ในรูปแบบที่เป็นมาตรฐานเดียวกัน พร้อมตรวจสอบคุณภาพของข้อมูล และเชื่อมโยงข้อมูลจากหลายแหล่งเข้าด้วยกันเพื่อเตรียมพร้อมสำหรับการวิเคราะห์ในขั้นตอนถัดไป

งานที่รับผิดชอบแบ่งออกเป็น 3 ส่วนหลัก ได้แก่

1. **Data Transformation:** แปลงข้อมูล Flood, Damage, Household Income และ Village Mapping ให้อยู่ในรูปแบบที่เหมาะสมต่อการวิเคราะห์
2. **Data Integration:** เชื่อมโยงข้อมูล Flood และ Household Income เข้ากับ Village Mapping โดยใช้รหัสหมู่บ้านหรือข้อมูลตำแหน่งทางการปกครอง
3. **Data Quality and Validation:** ตรวจสอบจำนวนแถว ความถูกต้องของชนิดข้อมูล ข้อมูลสูญหาย ความซ้ำซ้อน และผลลัพธ์หลังการเชื่อมโยงข้อมูล

หลักการสำคัญในการทำงานคือ การรักษาข้อมูลต้นฉบับให้มากที่สุด ไม่สร้างข้อมูลขึ้นมาแทนค่าที่ขาดหาย และไม่จับคู่ข้อมูลที่ไม่มีหลักฐานเพียงพอ

---

# 2. Project Research Questions

กระบวนการ Transformation และ Integration ถูกออกแบบมาเพื่อสนับสนุน Research Questions ของโครงงาน ได้แก่

### Q1: Which areas in Chiang Mai are most affected by floods, and how do damage patterns change year to year?

ต้องการศึกษาว่าพื้นที่ใดในจังหวัดเชียงใหม่ได้รับผลกระทบจากน้ำท่วมมากที่สุด และรูปแบบความเสียหายเปลี่ยนแปลงอย่างไรระหว่างปี

ข้อมูลที่เกี่ยวข้อง:
- Flood 2566
- Flood 2567
- Damage Records
- Village Mapping

การเตรียมข้อมูล:
- รวมข้อมูลน้ำท่วมจากปี 2566 และ 2567
- คัดเลือกข้อมูลเฉพาะจังหวัดเชียงใหม่
- เชื่อมโยงข้อมูลน้ำท่วมกับข้อมูลหมู่บ้าน
- รักษาข้อมูลปีและข้อมูลความเสียหายไว้เพื่อใช้เปรียบเทียบ

### Q2: Are geographic and demographic characteristics related to flood impacts?

ต้องการศึกษาความสัมพันธ์ระหว่างลักษณะทางภูมิศาสตร์ ประชากร และผลกระทบจากน้ำท่วม

ข้อมูลที่เกี่ยวข้อง:
- Flood Records
- Village Mapping
- Household Income

การเตรียมข้อมูล:
- เชื่อมโยง Flood กับข้อมูลพิกัด ประชากร และลักษณะภูมิศาสตร์ของหมู่บ้าน
- เชื่อมโยง Household Income กับข้อมูลหมู่บ้านเท่าที่สามารถจับคู่ได้อย่างน่าเชื่อถือ
- แยกข้อมูลที่จับคู่ไม่ได้และข้อมูลที่มีความกำกวมออกจากข้อมูลที่จับคู่ได้

### Q3: How should aid priority areas be ranked?

ต้องการเตรียมข้อมูลสำหรับจัดลำดับความสำคัญของพื้นที่ที่ควรได้รับความช่วยเหลือ

ข้อมูลที่เกี่ยวข้อง:
- Flood Records
- Damage Records
- Population
- Households
- Geographic Characteristics
- Household Income

การเตรียมข้อมูล:
- รักษาตัวเลขผู้ได้รับผลกระทบและความเสียหาย
- เชื่อมโยงข้อมูลประชากรและลักษณะพื้นที่
- เก็บข้อมูลรายได้ครัวเรือนไว้เป็นบริบททางเศรษฐกิจและสังคม
- ไม่กำหนดคะแนนหรืออันดับความช่วยเหลือในขั้น Transformation เพราะเป็นขั้นตอนวิเคราะห์ที่ต้องกำหนดเกณฑ์เพิ่มเติม

---

# 3. Directory Structure

โครงสร้างโฟลเดอร์ที่ใช้ในงานนี้

```text
transformation/
│
├── README.md
│
├── scripts/
│   ├── transform_flood.py
│   ├── transform_damage.py
│   ├── transform_household_income.py
│   ├── transform_village_mapping.py
│   ├── integrate_flood_mapping.py
│   ├── integrate_household_income_mapping.py
│   ├── profile_datasets.py
│   ├── profile_chiangmai_damage.py
│   ├── check_mapping_coverage.py
│   └── check_unmatched_codes.py
│
├── output/
│   ├── flood_2566_transformed.csv
│   ├── flood_2567_transformed.csv
│   ├── flood_chiangmai_combined.csv
│   ├── chiangmai_damage_transformed.csv
│   ├── household_income_transformed.csv
│   ├── village_mapping_transformed.csv
│   ├── flood_mapping_integrated.csv
│   └── household_income_mapping_integrated.csv
│
├── reports/
│   ├── flood_transformation_report.json
│   ├── damage_transformation_report.json
│   ├── household_income_transformation_report.json
│   ├── village_mapping_transformation_report.json
│   ├── flood_mapping_integration_report.json
│   └── household_income_mapping_integration_report.json
│
└── backup/
    ├── scripts/
    ├── output/
    ├── reports/
    └── README.md
```

หมายเหตุ:

- `scripts/` จัดเก็บ Python scripts สำหรับ Transformation และ Integration
- `output/` จัดเก็บข้อมูลที่ผ่านการประมวลผลแล้ว
- `reports/` จัดเก็บผลการตรวจสอบและสรุปการประมวลผลในรูปแบบ JSON
- `backup/` จัดเก็บไฟล์จากงาน Transformation ชุดเดิม แยกออกจาก Pipeline ปัจจุบัน ไม่ใช่ Output ของ Pipeline เชียงใหม่ชุดนี้

---

# 4. Input Datasets

ข้อมูลต้นทางที่ใช้ในกระบวนการนี้อยู่ภายใน `validation/cleaned/`

| Dataset | File | Description |
|---|---|---|
| Flood 2566 | `flood_2566_cleaned.csv` | ข้อมูลเหตุการณ์น้ำท่วมปี 2566 |
| Flood 2567 | `flood_2567_cleaned.csv` | ข้อมูลเหตุการณ์น้ำท่วมปี 2567 |
| Damage | `chiangmai_damage_cleaned.csv` | ข้อมูลความเสียหายจากภัยพิบัติในจังหวัดเชียงใหม่ |
| Household Income | `household_income_cleaned.csv` | ข้อมูลรายได้และจำนวนครัวเรือน |
| Village Mapping | `village_mapping_cleaned.csv` | ข้อมูลรหัสหมู่บ้าน ประชากร พิกัด และลักษณะภูมิศาสตร์ |
| Geographic Data | `Geographic_Data_deduplicated.csv` | ข้อมูลภูมิศาสตร์อีกชุดหนึ่ง ซึ่งไม่ได้ใช้ใน Pipeline เชียงใหม่ที่อธิบายในเอกสารนี้ |

**Important:** Input Datasets เป็นข้อมูลที่ผ่าน Cleaning และ Validation มาแล้ว ขั้น Transformation จึงเน้นการจัดรูปแบบ การแปลงชนิดข้อมูล การตรวจสอบ และการเชื่อมโยงข้อมูล ไม่ได้ทำหน้าที่แทนกระบวนการ Cleaning ต้นทางทั้งหมด

---

# 5. Data Transformation

## 5.1 Flood Data Transformation

**Script:** `scripts/transform_flood.py`

**Input:**
- `validation/cleaned/flood_2566_cleaned.csv`
- `validation/cleaned/flood_2567_cleaned.csv`

**Output:**
- `output/flood_2566_transformed.csv`
- `output/flood_2567_transformed.csv`
- `output/flood_chiangmai_combined.csv`

**Report:**
- `reports/flood_transformation_report.json`

### Objective

เตรียมข้อมูลเหตุการณ์น้ำท่วมจากสองปีให้อยู่ในรูปแบบที่สอดคล้องกัน และคัดเลือกข้อมูลเฉพาะจังหวัดเชียงใหม่เพื่อใช้ในการวิเคราะห์

### Transformation Rules

1. **Data Type Standardization**

   จัดชนิดข้อมูลให้เหมาะสมกับการนำไปวิเคราะห์ เช่น ข้อมูลตัวเลขและวันที่

   เหตุผล:
   - ป้องกันปัญหาการนำข้อมูลตัวเลขที่ถูกเก็บเป็นข้อความไปคำนวณ
   - ทำให้สามารถกรอง เรียงลำดับ และคำนวณข้อมูลได้ถูกต้อง
   - ทำให้ข้อมูลจากสองปีมีรูปแบบที่สอดคล้องกัน

2. **Preserving Identification Codes**

   เก็บรหัสหมู่บ้าน (`village_code`) เป็นข้อมูลประเภท String

   เหตุผล:
   - รหัสหมู่บ้านเป็น Identifier ไม่ใช่ตัวเลขสำหรับคำนวณ
   - การเก็บเป็นตัวเลขอาจทำให้เลขศูนย์ด้านหน้าหายไป
   - ต้องรักษารหัสให้ตรงกับ Village Mapping เพื่อใช้ Join ในภายหลัง

3. **Province Filtering**

   เลือกเฉพาะข้อมูลจังหวัดเชียงใหม่สำหรับชุดข้อมูลที่จะใช้วิเคราะห์ในโครงงาน

   เหตุผล:
   - ขอบเขตการศึกษาของโครงงานคือจังหวัดเชียงใหม่
   - การใช้ข้อมูลจังหวัดอื่นอาจทำให้ผลการวิเคราะห์ไม่ตรงกับขอบเขตการศึกษา
   - ลดข้อมูลที่ไม่เกี่ยวข้องกับ Research Questions

4. **Combining Multiple Years**

   รวมข้อมูล Flood ปี 2566 และ 2567 หลังจากแปลงให้อยู่ในรูปแบบมาตรฐานแล้ว

   เหตุผล:
   - ต้องการเปรียบเทียบรูปแบบผลกระทบระหว่างปี
   - ใช้โครงสร้างข้อมูลที่สอดคล้องกัน
   - ยังคงเก็บข้อมูลปีต้นทางไว้ ไม่รวมข้อมูลโดยทำให้แยกปีไม่ได้

5. **Missing Value Preservation**

   ไม่แทนค่าที่ไม่มีข้อมูลด้วยศูนย์โดยอัตโนมัติ

   เหตุผล:
   - ค่าศูนย์หมายถึงไม่มีเหตุการณ์หรือไม่มีปริมาณ
   - Missing หมายถึงไม่มีข้อมูลหรือไม่ได้ระบุ
   - สองกรณีนี้มีความหมายต่างกันในการวิเคราะห์

### Results

| Dataset | Input Rows | Output Rows |
|---|---:|---:|
| Flood 2566 | 19,584 | 1,198 |
| Flood 2567 | 34,875 | 3,556 |
| Combined | - | 4,754 |

ผลลัพธ์ Combined มีทั้งหมด 4,754 แถว

ข้อมูลรหัสหมู่บ้านไม่มี Missing Value ในชุด Combined ที่ใช้ทำ Integration

---

## 5.2 Damage Data Transformation

**Script:** `scripts/transform_damage.py`

**Input:**
- `validation/cleaned/chiangmai_damage_cleaned.csv`

**Output:**
- `output/chiangmai_damage_transformed.csv`

**Report:**
- `reports/damage_transformation_report.json`

### Objective

จัดรูปแบบข้อมูลความเสียหายให้อยู่ในโครงสร้างมาตรฐาน โดยรักษาข้อมูลเกี่ยวกับผู้ได้รับผลกระทบ การอพยพ การสูญเสียชีวิต และความเสียหายต่อบ้านเรือน

### Transformation Rules

1. **Column Standardization**

   เปลี่ยนชื่อคอลัมน์ให้สื่อความหมายและใช้งานสะดวกขึ้น เช่น

   | Original Column | Transformed Column |
   |---|---|
   | ปี | `source_year` |
   | อำเภอ | `district` |
   | ตำบล | `subdistrict_id` |
   | หมู่บ้าน | `village_id` |
   | วันที่เกิดภัย | `disaster_date` |
   | ราษฎร(คน) | `affected_people` |
   | ราษฎร(ครัวเรือน) | `affected_households` |
   | อพยพ(ครัวเรือน) | `evacuated_households` |
   | อพยพ(คน) | `evacuated_people` |
   | เสียชีวิต(คน) | `deaths` |
   | สูญหาย(คน) | `missing_people` |
   | บาดเจ็บ(คน) | `injured_people` |
   | บ้านพักอาศัย(หลัง) | `houses_damaged` |
   | บ้านเรือนบางส่วน(หลัง) | `partially_damaged_houses` |

2. **Source Record Identification**

   สร้าง `source_record_id` เพื่อใช้ระบุแถวข้อมูลต้นทาง

   เหตุผล:
   - ช่วยติดตามข้อมูลกลับไปยังรายการต้นทาง
   - ช่วยตรวจสอบข้อมูลที่มีลักษณะซ้ำกัน
   - ไม่จำเป็นต้องลบข้อมูลที่มีตำแหน่งและวันที่เหมือนกันทันที

3. **Date Conversion**

   แปลงวันที่เกิดภัยให้อยู่ในรูปแบบวันที่ที่สามารถประมวลผลได้

   ผลตรวจสอบ:
   - วันที่แปลงไม่สำเร็จ: 0
   - วันที่หายไป: 0

4. **Numeric Conversion**

   แปลงจำนวนประชากร จำนวนครัวเรือน และตัวเลขความเสียหายให้เป็นข้อมูลตัวเลข

   ผลตรวจสอบ:
   - ไม่พบ Numeric Conversion Errors ในคอลัมน์ที่ตรวจสอบ

5. **Missing Values**

   พบค่า Missing ใน `partially_damaged_houses` จำนวน 302 แถว

   การตัดสินใจ:
   - ไม่แทนค่า Missing ด้วย 0
   - ไม่สมมติว่าบ้านเรือนบางส่วนไม่มีความเสียหาย
   - เก็บ Missing ไว้เพื่อสะท้อนข้อจำกัดของข้อมูลต้นทาง

   เหตุผล:
   การไม่มีข้อมูลจำนวนบ้านเรือนที่เสียหายบางส่วนไม่ได้หมายความว่าค่าความเสียหายเป็นศูนย์ หากเติม 0 โดยไม่มีหลักฐาน อาจทำให้การประเมินความเสียหายต่ำกว่าความเป็นจริง

6. **Duplicate Investigation**

   พบรายการที่มีลักษณะซ้ำกันตามเกณฑ์ Location/Date จำนวน 25 รายการในรายงาน

   การตัดสินใจ:
   - ไม่ลบรายการเหล่านี้โดยอัตโนมัติ
   - เก็บข้อมูลทั้งหมดไว้
   - ต้องตรวจสอบบริบทของเหตุการณ์ก่อนสรุปว่าเป็น Duplicate จริง

   เหตุผล:
   พื้นที่เดียวกันอาจเกิดเหตุการณ์หรือมีรายงานความเสียหายหลายรายการได้ การลบข้อมูลเพียงเพราะมีตำแหน่งและวันที่ตรงกันอาจทำให้ข้อมูลจริงสูญหาย

### Results

| Metric | Result |
|---|---:|
| Input Rows | 866 |
| Output Rows | 866 |
| Output Columns | 15 |
| Missing `partially_damaged_houses` | 302 |
| Missing `disaster_date` | 0 |
| Date Conversion Errors | 0 |
| Numeric Conversion Errors | 0 |
| Potential Duplicate Location/Date Records | 25 |

**Important limitation:**

`subdistrict_id` และ `village_id` ใน Damage Dataset เป็นรหัสท้องถิ่นแบบสั้น ไม่ใช่ `village_code` เต็มรูปแบบของ Village Mapping

ดังนั้นจึงยังไม่นำ Damage Dataset ไป Join กับ Village Mapping โดยตรง เพราะอาจเกิดการจับคู่ผิดพื้นที่

การเชื่อมโยงในอนาคตต้องมีตารางอ้างอิงหรือหลักฐานที่ยืนยันความสัมพันธ์ของรหัสก่อน

---

## 5.3 Household Income Transformation

**Script:** `scripts/transform_household_income.py`

**Input:**
- `validation/cleaned/household_income_cleaned.csv`

**Output:**
- `output/household_income_transformed.csv`

**Report:**
- `reports/household_income_transformation_report.json`

### Objective

เตรียมข้อมูลรายได้ครัวเรือนให้อยู่ในรูปแบบที่สามารถนำไปวิเคราะห์ร่วมกับข้อมูลประชากรและภูมิศาสตร์ได้

### Transformation Rules

1. **Column Standardization**

   จัดชื่อคอลัมน์ให้อยู่ในรูปแบบที่สอดคล้องกัน เช่น

   - `statistic`
   - `district`
   - `subdistrict`
   - `area`
   - `households`
   - `income`
   - `unit`

2. **Numeric Conversion**

   แปลงจำนวนครัวเรือนและรายได้ให้เป็นตัวเลข

   ผลตรวจสอบ:
   - `households` conversion errors = 0
   - `income` conversion errors = 0

3. **Preserving Measurement Unit**

   เก็บข้อมูลหน่วยรายได้เป็น `บาท/ปี`

   เหตุผล:
   - หน่วยเป็นส่วนสำคัญของความหมายของข้อมูล
   - ป้องกันการตีความรายได้ผิดช่วงเวลา
   - ทำให้ผู้วิเคราะห์ทราบว่าค่ารายได้เป็นข้อมูลต่อปี

4. **Preserving Original Area Names**

   รักษาชื่อพื้นที่จากต้นทาง เช่น `ทุ่งปี๊`

   ไม่เปลี่ยนเป็นชื่อที่ดูคล้ายกัน เช่น `ทุ่งปี้` โดยไม่มีหลักฐานยืนยัน

   เหตุผล:
   - ชื่อพื้นที่เป็นข้อมูลสำคัญสำหรับการ Join
   - การแก้ชื่อเองอาจทำให้ข้อมูลถูกจับคู่กับพื้นที่ผิด
   - ต้องรักษาความถูกต้องของข้อมูลต้นทาง

5. **No Year Assignment**

   Dataset นี้ไม่มีคอลัมน์ปี

   จึงไม่กำหนดปีให้ข้อมูลรายได้เอง และไม่ถือว่าข้อมูลนี้เป็นรายได้ของปี 2566 หรือ 2567

   ข้อมูลรายได้จะถูกใช้เป็นบริบทด้านเศรษฐกิจและสังคมเท่านั้น

### Results

| Metric | Result |
|---|---:|
| Input Rows | 2,154 |
| Output Rows | 2,154 |
| Output Columns | 7 |
| Households Conversion Errors | 0 |
| Income Conversion Errors | 0 |

---

## 5.4 Village Mapping Transformation

**Script:** `scripts/transform_village_mapping.py`

**Input:**
- `validation/cleaned/village_mapping_cleaned.csv`

**Output:**
- `output/village_mapping_transformed.csv`

**Report:**
- `reports/village_mapping_transformation_report.json`

### Objective

เตรียมข้อมูลหมู่บ้านให้เป็นตารางอ้างอิงกลางสำหรับเชื่อมโยงข้อมูล Flood และ Household Income

ข้อมูลสำคัญประกอบด้วย:
- Administrative Codes
- Village Names
- Latitude / Longitude
- Population
- Households
- Geographic Features

### Transformation Rules

1. **Identifier Preservation**

   เก็บรหัสพื้นที่ เช่น `province_code`, `district_code`, `subdistrict_code` และ `village_code` เป็น String

   เหตุผล:
   - เป็นรหัสสำหรับระบุพื้นที่ ไม่ใช่ตัวเลขสำหรับคำนวณ
   - ป้องกันการสูญเสียเลขศูนย์ด้านหน้า
   - รักษาความถูกต้องในการเชื่อมโยงข้อมูล

2. **Coordinate Preservation**

   เก็บ `latitude` และ `longitude` สำหรับใช้ระบุตำแหน่งหมู่บ้าน

   ผลตรวจสอบ:
   - ไม่พบพิกัดที่ Missing ในชุดข้อมูลที่ผ่าน Transformation

3. **Population and Household Conversion**

   แปลงข้อมูลประชากรและจำนวนครัวเรือนให้เหมาะสมกับการคำนวณ

   เช่น:
   - `population_total`
   - `women`
   - `men`
   - `households`

4. **Geographic Feature Standardization**

   รักษาข้อมูลลักษณะทางภูมิศาสตร์ เช่น
   - River
   - Mountain
   - Swamp
   - Dam
   - Reservoir

   โดยเก็บทั้ง Flag และ Name เช่น `river_flag` และ `river_name`

   เหตุผล:
   - Flag ใช้ระบุว่ามีคุณลักษณะนั้นหรือไม่
   - Name ใช้ระบุรายละเอียดของคุณลักษณะ
   - ไม่ควรแทนข้อมูลชื่อด้วยค่า Flag เพียงอย่างเดียว

5. **Road Number Data Type Decision**

   ในการตรวจสอบพบว่า `road_number` และ `road_number_2` มีข้อมูลหลายรูปแบบ เช่น

   - `ชม. 4016`
   - `107,1178`
   - `ถนนทางหลวงชนบท ชม.3009`
   - `-`

   การตัดสินใจ:
   - เก็บสองคอลัมน์นี้เป็นข้อความ (String)
   - ไม่บังคับแปลงเป็นตัวเลข

   เหตุผล:
   - ข้อมูลถนนมีทั้งตัวเลข ตัวอักษร เครื่องหมาย และรายละเอียดชื่อถนน
   - ไม่ใช่ตัวเลขเชิงปริมาณที่นำไปคำนวณโดยตรง
   - การบังคับแปลงอาจทำให้ข้อมูลสูญหายหรือเกิด Conversion Errors

6. **Mountain Elevation Conversion**

   พบค่า `mountain_elevation` ที่มีเครื่องหมายคอมมาคั่นหลักพัน เช่น `1,100`

   จึงลบเครื่องหมายคอมมาก่อนแปลงเป็นตัวเลข

   เหตุผล:
   - เครื่องหมายคอมมาเป็นตัวคั่นหลักพัน ไม่ใช่ส่วนหนึ่งของค่าความสูง
   - ต้องการให้ข้อมูลอยู่ในรูปแบบ Numeric สำหรับการวิเคราะห์

7. **Duplicate and Missing Identifier Checks**

   ตรวจสอบ `mcode` และรหัสหมู่บ้านที่ใช้เป็น Identifier

   ผลตรวจสอบ:
   - ไม่มี Missing `mcode`
   - ไม่มี Duplicate `mcode`
   - ไม่มี Missing Coordinates

8. **Quarantine Handling**

   ไม่รวมข้อมูลจาก `village_mapping_quarantine.json` เข้ามาใน Mapping หลัก

   เหตุผล:
   - Quarantine เป็นข้อมูลที่ถูกแยกออกจากชุดข้อมูลหลัก
   - ยังไม่ควรนำข้อมูลที่ยังไม่ผ่านเกณฑ์มาใช้เป็นข้อมูลอ้างอิงที่เชื่อถือได้
   - ป้องกันการสร้างความสัมพันธ์ระหว่างพื้นที่โดยไม่มีหลักฐานเพียงพอ

### Results

| Metric | Result |
|---|---:|
| Input Rows | 2,184 |
| Output Rows | 2,184 |
| Output Columns | 75 |
| Province Code | 50 for all records |
| Missing `mcode` | 0 |
| Duplicate `mcode` | 0 |
| Missing Coordinates | 0 |
| Road Number Conversion Errors | 0 |
| Mountain Elevation Conversion Errors | 0 |

---

# 6. Data Integration

Data Integration เป็นขั้นตอนเชื่อมโยงข้อมูลจากหลาย Dataset เข้าด้วยกัน โดยใช้ Village Mapping เป็นข้อมูลอ้างอิงด้านพื้นที่

การเลือก Join Key ต้องพิจารณาจากความหมายของข้อมูล ความถูกต้องของ Identifier และความสามารถในการยืนยันว่าข้อมูลสองชุดอ้างถึงพื้นที่เดียวกันจริง

ไม่ใช้เพียงการทำให้ชื่อคล้ายกันเพื่อเพิ่ม Match Rate

---

## 6.1 Flood and Village Mapping Integration

**Script:** `scripts/integrate_flood_mapping.py`

**Input:**
- `output/flood_chiangmai_combined.csv`
- `output/village_mapping_transformed.csv`

**Output:**
- `output/flood_mapping_integrated.csv`

**Report:**
- `reports/flood_mapping_integration_report.json`

### Objective

เชื่อมโยงข้อมูลน้ำท่วมกับข้อมูลหมู่บ้าน เพื่อเพิ่มบริบทด้านตำแหน่ง ประชากร และลักษณะทางภูมิศาสตร์ให้กับ Flood Records

### Join Key Decision

เลือก `village_code` เป็น Join Key

เหตุผล:
1. เป็นรหัสที่ใช้ระบุหมู่บ้านโดยตรง
2. มีอยู่ในทั้ง Flood และ Village Mapping
3. มีความน่าเชื่อถือมากกว่าการใช้ชื่อหมู่บ้านเพียงอย่างเดียว
4. ลดปัญหาชื่อซ้ำหรือชื่อสะกดต่างกัน

ก่อน Join มีการตรวจสอบว่า:
- Mapping ไม่มี Missing `village_code`
- Mapping ไม่มี Duplicate `village_code`
- Flood ไม่มี Missing `village_code`

หากพบข้อผิดพลาดดังกล่าว Script จะหยุดทำงานด้วย ValueError แทนการ Join ต่อโดยไม่ตรวจสอบ

### Join Type Decision: Left Join

เลือกใช้ Left Join โดยกำหนด Flood เป็น Left Dataset และ Village Mapping เป็น Right Dataset

เหตุผล:
- Flood เป็นข้อมูลหลักที่ต้องการศึกษา
- ต้องเก็บทุกเหตุการณ์น้ำท่วมไว้
- แม้บางเหตุการณ์จะไม่มีข้อมูล Mapping ก็ไม่ควรถูกลบออก
- การใช้ Inner Join อาจทำให้ Flood Records ที่ไม่สามารถจับคู่ได้สูญหาย

### Join Validation: many_to_one

ใช้ `validate="many_to_one"`

ความหมาย:
- Flood หลายรายการสามารถอ้างถึงหมู่บ้านเดียวกันได้
- แต่ Mapping หนึ่ง `village_code` ต้องมีเพียงหนึ่งรายการ

เหตุผล:
- เหตุการณ์น้ำท่วมหลายครั้งสามารถเกิดในหมู่บ้านเดียวกันได้
- ไม่ควรมี Mapping หลายแถวสำหรับรหัสหมู่บ้านเดียวกัน เพราะจะทำให้ข้อมูล Flood เพิ่มจำนวนแถวโดยไม่ตั้งใจ

### Selected Mapping Attributes

เลือกเฉพาะข้อมูลที่มีประโยชน์ต่อการวิเคราะห์ ได้แก่

**Village Identification**
- `village_name`

**Coordinates**
- `latitude`
- `longitude`

**Demographics**
- `population_total`
- `women`
- `men`
- `households`

**Geographic Features**
- `river_flag`
- `river_name`
- `mountain_flag`
- `mountain_name`
- `swamp_flag`
- `swamp_name`
- `dam_flag`
- `dam_name`
- `reservoir_flag`
- `reservoir_name`

เหตุผลที่เลือกเฉพาะบางคอลัมน์:
- ลดข้อมูลที่ไม่จำเป็นต่อการวิเคราะห์
- ลดความซ้ำซ้อนของข้อมูลระหว่าง Dataset
- เพิ่มเฉพาะคุณลักษณะที่เกี่ยวข้องกับ Research Questions

### Match Status

สร้างคอลัมน์ `mapping_match_status`

| Status | Meaning |
|---|---|
| `matched` | พบ Village Mapping ที่ตรงกับ `village_code` |
| `unmatched` | ไม่พบ Village Mapping ที่ตรงกับ `village_code` |

ไม่เติมข้อมูลที่ไม่มีใน Mapping และไม่สร้างค่าพิกัดหรือข้อมูลประชากรขึ้นเอง

### Integration Results

| Metric | Result |
|---|---:|
| Flood Input Rows | 4,754 |
| Mapping Input Rows | 2,184 |
| Integrated Output Rows | 4,754 |
| Matched Rows | 4,721 |
| Unmatched Rows | 33 |
| Match Rate | 99.31% |
| Unmatched Unique Village Codes | 13 |
| Output Columns | 69 |

### Interpretation

Match Rate 99.31% หมายถึง 4,721 จาก 4,754 Flood Records สามารถเชื่อมโยงกับ Village Mapping ได้

มี 33 Records ที่ไม่สามารถจับคู่ได้ โดยมีรหัสหมู่บ้านที่ไม่ซ้ำกัน 13 รหัส

จำนวน 33 คือจำนวนแถวข้อมูล ส่วน 13 คือจำนวนรหัสที่ไม่ซ้ำกัน จึงเป็นคนละตัวชี้วัด

การตัดสินใจ:
- เก็บ Unmatched Records ไว้
- ไม่ลบข้อมูล
- ไม่เติมค่าจากพื้นที่อื่น
- ไม่ใช้ข้อมูล Quarantine เป็นข้อมูล Mapping หลัก

---

## 6.2 Household Income and Village Mapping Integration

**Script:** `scripts/integrate_household_income_mapping.py`

**Input:**
- `output/household_income_transformed.csv`
- `output/village_mapping_transformed.csv`

**Output:**
- `output/household_income_mapping_integrated.csv`

**Report:**
- `reports/household_income_mapping_integration_report.json`

### Objective

เชื่อมโยงรายได้ครัวเรือนกับข้อมูลประชากรและภูมิศาสตร์ของหมู่บ้าน เพื่อเตรียมข้อมูลบริบทด้านเศรษฐกิจและสังคมสำหรับการวิเคราะห์

### Challenge: No Direct Village Code

Household Income Dataset ไม่มี `village_code` ที่สามารถใช้ Join กับ Village Mapping ได้โดยตรง

จึงต้องใช้ข้อมูลชื่อพื้นที่แทน

การใช้ชื่อพื้นที่มีความเสี่ยง เช่น:
- ชื่อหมู่บ้านเหมือนกันในตำบลเดียวกัน
- ชื่อหมู่บ้านมีข้อความเพิ่มเติมในวงเล็บ
- การสะกดชื่อแตกต่างกัน
- ชื่อชุมชนไม่ตรงกับชื่อหมู่บ้านใน Mapping

ดังนั้นจึงต้องสร้าง Matching Key และกำหนดเกณฑ์ความน่าเชื่อถือก่อน Join

### Matching Key Decision

ใช้ข้อมูล 3 ส่วนร่วมกัน ได้แก่

1. `district`
2. `subdistrict`
3. `area`

สร้าง Composite Key จากทั้งสามฟิลด์

เหตุผล:
- การใช้ชื่อหมู่บ้านเพียงอย่างเดียวมีโอกาสชนกันสูง
- การเพิ่มอำเภอและตำบลช่วยจำกัดขอบเขตพื้นที่
- ลดโอกาสจับคู่หมู่บ้านชื่อเดียวกันที่อยู่คนละพื้นที่

ตัวอย่างแนวคิด:

```text
(district, subdistrict, area)
```

### Normalization Rules

กำหนดกฎการปรับข้อความดังนี้

**1. Trim Whitespace**

ตัดช่องว่างด้านหน้าและด้านหลังของข้อความ

ตัวอย่าง:

```text
" สารภี " → "สารภี"
```

เหตุผล:
ช่องว่างที่ไม่จำเป็นไม่ควรทำให้ข้อมูลที่มีชื่อเดียวกันกลายเป็นคนละ Key

**2. Remove Leading บ้าน**

ตัดคำว่า `บ้าน` เฉพาะกรณีที่อยู่ด้านหน้าของชื่อพื้นที่

ตัวอย่าง:

```text
"บ้าน ป่าป้อง" → "ป่าป้อง"
"ป่าป้อง"      → "ป่าป้อง"
```

เหตุผล:
ข้อมูลจากสอง Dataset อาจมีรูปแบบการเขียนคำนำหน้าหมู่บ้านต่างกัน

**3. Preserve Parentheses**

เก็บข้อความในวงเล็บไว้ ไม่ลบออก

ตัวอย่าง:

```text
"บ้าน ป่าป้อง (หมู่ 3)"
"บ้าน ป่าป้อง (หมู่ 4)"
```

ไม่เปลี่ยนทั้งสองรายการให้เป็นชื่อเดียวกัน

เหตุผล:
ข้อความในวงเล็บอาจมีข้อมูลสำคัญ เช่น หมู่ที่ หรือชื่อหน่วยงาน การลบออกอาจทำให้หมู่บ้านที่แตกต่างกันกลายเป็น Matching Key เดียวกัน

**4. No Automatic Spelling Correction**

ไม่แก้ชื่อพื้นที่ที่สะกดแตกต่างกันโดยอัตโนมัติ

เหตุผล:
ชื่อที่คล้ายกันไม่ได้หมายความว่าเป็นพื้นที่เดียวกัน การแก้ชื่อโดยไม่มีหลักฐานอาจทำให้เกิด False Match

### Matching Classification

ก่อน Join จะนับจำนวน Mapping Records ที่มี Composite Key เดียวกัน

จากนั้นแบ่งออกเป็น 3 สถานะ

**1. Unique Match**

กำหนดเมื่อ Matching Key พบใน Village Mapping เพียงหนึ่งรายการ

```text
Mapping Key Count = 1
```

การตัดสินใจ:
- สามารถ Join ข้อมูล Mapping ได้
- ใช้ข้อมูลจาก Mapping แถวนั้นเพียงรายการเดียว
- ตรวจสอบด้วย `validate="many_to_one"`

เหตุผล:
มี Mapping Candidate เพียงหนึ่งรายการ จึงไม่มีความกำกวมจากการเลือกหลายหมู่บ้านที่ใช้ชื่อเดียวกันภายใต้ Key เดียวกัน

**2. Ambiguous**

กำหนดเมื่อ Matching Key พบใน Village Mapping มากกว่าหนึ่งรายการ

```text
Mapping Key Count > 1
```

การตัดสินใจ:
- ไม่เลือก Mapping แถวแรก
- ไม่สุ่มเลือก Village Code
- ไม่ Join ข้อมูล Mapping ให้กับ Income Record
- เก็บ Income Record ไว้และกำหนดสถานะ `ambiguous`

เหตุผล:
การเลือก Mapping เพียงหนึ่งรายการจากหลาย Candidate โดยไม่มีหลักฐานอาจทำให้รายได้ถูกเชื่อมกับประชากรหรือพิกัดของหมู่บ้านผิดแห่ง

**3. Unmatched**

กำหนดเมื่อไม่พบ Matching Key ใน Village Mapping

```text
Mapping Key Count = 0
```

การตัดสินใจ:
- เก็บ Income Record ไว้
- กำหนดสถานะ `unmatched`
- ไม่เติม Village Code หรือข้อมูลภูมิศาสตร์

เหตุผล:
ชื่อที่ไม่ตรงกันอาจเป็นชื่อชุมชน ชื่อท้องถิ่น หรือชื่อที่มีรูปแบบแตกต่างกัน จึงไม่ควรบังคับจับคู่

### Left Join Decision

เลือกใช้ Left Join โดยกำหนด Household Income เป็น Left Dataset

เหตุผล:
- ต้องการเก็บข้อมูลรายได้ทุกแถว
- ไม่ควรทำให้ข้อมูลต้นทางสูญหายเพราะ Mapping ไม่ตรง
- ต้องการให้ผู้วิเคราะห์สามารถแยกข้อมูลที่ Match และไม่ Match ได้

ก่อน Join จะเลือกเฉพาะ Mapping Records ที่มี Unique Key เท่านั้น

จึงไม่ทำให้แถว Income เพิ่มขึ้นจาก Mapping ที่มีชื่อซ้ำ

### Selected Mapping Attributes

เพิ่มข้อมูลจาก Village Mapping ได้แก่

**Identification**
- `village_code`
- `district_code`
- `subdistrict_code`

**Coordinates**
- `latitude`
- `longitude`

**Demographics**
- `population_total`
- `women`
- `men`

**Household Information**
- `mapping_households`

**Geographic Features**
- `river_flag`
- `river_name`
- `mountain_flag`
- `mountain_name`
- `swamp_flag`
- `swamp_name`
- `dam_flag`
- `dam_name`
- `reservoir_flag`
- `reservoir_name`

เพื่อป้องกันชื่อคอลัมน์ชนกันระหว่าง Income และ Mapping:

- `households` หมายถึงจำนวนครัวเรือนจาก Household Income
- `mapping_households` หมายถึงจำนวนครัวเรือนจาก Village Mapping

### Integration Results

| Metric | Result |
|---|---:|
| Income Input Rows | 2,154 |
| Mapping Input Rows | 2,184 |
| Integrated Output Rows | 2,154 |
| Unique Match Rows | 1,448 |
| Ambiguous Rows | 28 |
| Unmatched Rows | 678 |
| Unique Match Rate | 67.22% |
| Ambiguous Rate | 1.30% |
| Unmatched Rate | 31.48% |
| Unique Matched Village Codes | 1,446 |
| Output Columns | 27 |

### Interpretation

จาก Income ทั้งหมด 2,154 Records:

- 1,448 Records สามารถจับคู่กับ Mapping ที่มี Candidate เพียงหนึ่งรายการ
- 28 Records มี Mapping Candidate มากกว่าหนึ่งรายการ
- 678 Records ไม่พบ Mapping ที่ตรงกับ Composite Key

มี Unique Match 1,448 Records แต่มี Unique Village Codes 1,446 รหัส เนื่องจาก Income มีบางพื้นที่ปรากฏซ้ำหลายแถว

ตัวอย่างที่ตรวจพบคือ:

```text
อำเภอ: สารภี
ตำบล: หนองแฝก
พื้นที่: บ้าน หนองแฝก
จำนวนรายการ: 3 แถว
```

การตัดสินใจ:
- เก็บทั้ง 3 แถว
- ไม่ลบข้อมูลซ้ำโดยอัตโนมัติ
- เนื่องจากยังไม่มีหลักฐานยืนยันว่าเป็นข้อมูลซ้ำที่ผิดพลาด

### Why Match Rate Is Not Forced to 100%

การได้ Match Rate สูงไม่ได้หมายความว่าข้อมูลถูกต้องเสมอไป

สำหรับ Income Dataset การใช้กฎที่เข้มงวดมีความสำคัญกว่าการจับคู่ให้ได้มากที่สุด

หากลบวงเล็บ แก้ชื่อสะกดเอง หรือเลือก Mapping Candidate แบบสุ่ม อาจเพิ่มจำนวน Match แต่ทำให้ข้อมูลรายได้ถูกเชื่อมกับหมู่บ้านผิดแห่ง

ดังนั้นจึงเลือกเก็บข้อมูลที่ยังจับคู่ไม่ได้ไว้ และแสดงสถานะให้ตรวจสอบภายหลัง

---

# 7. Data Quality and Validation Strategy

การตรวจสอบคุณภาพข้อมูลใช้หลักการดังต่อไปนี้

## 7.1 Row Count Preservation

ตรวจสอบจำนวนแถวก่อนและหลัง Transformation หรือ Integration

เหตุผล:
- ตรวจจับข้อมูลสูญหาย
- ตรวจจับการเพิ่มแถวจาก Join ที่ไม่ถูกต้อง
- ยืนยันว่ากระบวนการไม่ทำให้ข้อมูลต้นทางเปลี่ยนจำนวนโดยไม่ตั้งใจ

ผลตรวจสอบ:

| Dataset | Input Rows | Output Rows |
|---|---:|---:|
| Damage | 866 | 866 |
| Household Income | 2,154 | 2,154 |
| Village Mapping | 2,184 | 2,184 |
| Flood Integration | 4,754 | 4,754 |
| Income Integration | 2,154 | 2,154 |

## 7.2 Identifier Validation

ตรวจสอบรหัสที่ใช้ระบุพื้นที่ว่า:
- ไม่มี Missing Identifier
- ไม่มี Duplicate Identifier ในตารางอ้างอิง
- มีชนิดข้อมูลเหมาะสม
- ไม่สูญเสียเลขศูนย์ด้านหน้า

เหตุผล:
Identifier เป็นพื้นฐานของการเชื่อมโยงข้อมูล หากรหัสผิดเพียงบางหลักอาจทำให้ข้อมูลเชื่อมผิดพื้นที่ได้

## 7.3 Data Type Validation

ตรวจสอบว่าข้อมูลแต่ละประเภทถูกแปลงอย่างเหมาะสม

ตัวอย่าง:
- จำนวนประชากรเป็น Numeric
- รายได้เป็น Numeric
- วันที่เป็น Date
- รหัสพื้นที่เป็น String
- ชื่อถนนเป็น String

ไม่บังคับให้ทุกคอลัมน์ที่มีตัวเลขต้องเป็น Numeric เพราะต้องพิจารณาความหมายของข้อมูลด้วย

## 7.4 Missing Value Validation

ตรวจสอบจำนวน Missing Values และพิจารณาความหมายก่อนตัดสินใจจัดการ

หลักการ:
- Missing ไม่เท่ากับ Zero
- ไม่เติมค่าที่ไม่มีหลักฐาน
- เก็บ Missing ที่มีความหมายต่อการตีความข้อมูล
- รายงานข้อจำกัดของข้อมูลให้ผู้วิเคราะห์ทราบ

## 7.5 Join Validation

ตรวจสอบว่า:
- จำนวนแถวหลัง Join ถูกต้อง
- Join Key ตรงกับข้อมูลอ้างอิง
- Mapping ไม่มี Duplicate Key ในกรณีที่ต้องการ Many-to-One
- Unmatched Records ยังคงอยู่
- Ambiguous Records ไม่ได้รับการเลือก Mapping โดยพลการ

## 7.6 Report Validation

สร้าง JSON Report เพื่อเก็บรายละเอียด เช่น:
- Input Rows
- Output Rows
- Output Columns
- Matched Rows
- Unmatched Rows
- Match Rate
- Data Quality Notes

Report ใช้สำหรับตรวจสอบผลการประมวลผลและช่วยให้สามารถย้อนกลับมาทบทวนเหตุผลในการตัดสินใจได้

---

# 8. Important Data Limitations

ข้อจำกัดต่อไปนี้ควรได้รับการพิจารณาก่อนนำข้อมูลไปวิเคราะห์

## 8.1 Household Income Has No Year Field

Household Income Dataset ไม่มีข้อมูลปี

ดังนั้น:
- ไม่สามารถระบุได้จาก Dataset นี้เพียงอย่างเดียวว่ารายได้เป็นของปีใด
- ไม่ควรนำไปเปรียบเทียบรายได้ปี 2566 กับ 2567 โดยตรง
- ควรใช้เป็นบริบทด้านเศรษฐกิจและสังคมตามขอบเขตที่ข้อมูลรองรับ

## 8.2 Unmatched Income Records

มี Income Records จำนวน 678 แถวที่ไม่พบ Matching Key ใน Village Mapping

สาเหตุที่เป็นไปได้ ได้แก่:
- ชื่อหมู่บ้านไม่ตรงกัน
- ชื่อชุมชนแตกต่างจากชื่อหมู่บ้าน
- รูปแบบชื่อแตกต่างกัน
- ข้อมูลต้นทางใช้ชื่อพื้นที่คนละรูปแบบ

ยังไม่สรุปว่าข้อมูลเหล่านี้เป็นข้อมูลผิดพลาดทั้งหมด

ควรตรวจสอบเพิ่มเติมก่อนกำหนด Mapping ใหม่

## 8.3 Ambiguous Income Records

มี Income Records จำนวน 28 แถวที่มี Mapping Candidate มากกว่าหนึ่งรายการ

ยังไม่นำข้อมูลเหล่านี้ไปใช้เป็นข้อมูลที่จับคู่กับหมู่บ้านใดหมู่บ้านหนึ่งโดยตรง

หากต้องการแก้ไข ควรใช้หลักฐานเพิ่มเติม เช่น:
- หมู่ที่
- รหัสหมู่บ้าน
- เอกสารอ้างอิงจากหน่วยงาน
- พิกัดที่ยืนยันได้

## 8.4 Flood Unmatched Records

มี Flood Records จำนวน 33 แถวที่ไม่พบ Mapping โดยมีรหัสหมู่บ้านที่ไม่ซ้ำกัน 13 รหัส

ไม่ควรเติมข้อมูลภูมิศาสตร์จากพื้นที่ใกล้เคียงโดยอัตโนมัติ

## 8.5 Damage Local Identifiers

รหัส `subdistrict_id` และ `village_id` ใน Damage Dataset ไม่ใช่รหัสเดียวกับ `village_code` ของ Village Mapping

ต้องมี Reference Table ก่อนจึงจะสามารถ Join ได้อย่างน่าเชื่อถือ

## 8.6 Damage Missing Values

พบ Missing `partially_damaged_houses` จำนวน 302 แถว

ไม่ควรตีความว่าเป็นบ้านที่ไม่มีความเสียหายบางส่วน

## 8.7 Quarantined Mapping Records

ข้อมูล Quarantine ไม่ได้รวมอยู่ใน Village Mapping หลักที่ใช้ Integration

หากจะนำกลับมาใช้ต้องผ่านการตรวจสอบและยืนยันข้อมูลก่อน

## 8.8 Duplicate Records

การพบชื่อพื้นที่หรือวันที่เหมือนกันไม่ได้แปลว่าข้อมูลเป็น Duplicate ที่ต้องลบทิ้งเสมอไป

ควรพิจารณาความหมายของแต่ละรายการและ Source Record ก่อนลบข้อมูล

---

# 9. Execution Guide

## 9.1 Environment

ใช้ Python Virtual Environment และติดตั้ง Dependencies ที่โปรเจกต์กำหนด

ตัวอย่างการเปิด Environment:

```bash
source .venv/Scripts/activate
```

สำหรับ Windows Git Bash

ตรวจสอบ Python:

```bash
python --version
```

ตรวจสอบ pandas:

```bash
python -c "import pandas as pd; print(pd.__version__)"
```

## 9.2 Recommended Execution Order

ให้รัน Transformation ก่อน Integration ตามลำดับดังนี้

### Step 1: Transform Flood

```bash
python transformation/scripts/transform_flood.py
```

สร้าง:
- Flood 2566 Transformed
- Flood 2567 Transformed
- Flood Chiang Mai Combined

### Step 2: Transform Damage

```bash
python transformation/scripts/transform_damage.py
```

สร้าง:
- Chiang Mai Damage Transformed

### Step 3: Transform Household Income

```bash
python transformation/scripts/transform_household_income.py
```

สร้าง:
- Household Income Transformed

### Step 4: Transform Village Mapping

```bash
python transformation/scripts/transform_village_mapping.py
```

สร้าง:
- Village Mapping Transformed

### Step 5: Integrate Flood and Mapping

```bash
python transformation/scripts/integrate_flood_mapping.py
```

สร้าง:
- Flood Mapping Integrated
- Flood Mapping Integration Report

### Step 6: Integrate Household Income and Mapping

```bash
python transformation/scripts/integrate_household_income_mapping.py
```

สร้าง:
- Household Income Mapping Integrated
- Household Income Mapping Integration Report

**Important:** Integration Scripts ต้องใช้ Output จาก Transformation ก่อนหน้า ดังนั้นไม่ควรรัน Integration ก่อนที่ Input Files จะถูกสร้างหรืออัปเดตแล้ว

---

# 10. Final Output Summary

| Output Dataset | Rows | Purpose |
|---|---:|---|
| `flood_2566_transformed.csv` | 1,198 | Chiang Mai Flood 2566 |
| `flood_2567_transformed.csv` | 3,556 | Chiang Mai Flood 2567 |
| `flood_chiangmai_combined.csv` | 4,754 | Combined Flood Records |
| `chiangmai_damage_transformed.csv` | 866 | Damage Records |
| `household_income_transformed.csv` | 2,154 | Household Income |
| `village_mapping_transformed.csv` | 2,184 | Village Reference Data |
| `flood_mapping_integrated.csv` | 4,754 | Flood + Village Mapping |
| `household_income_mapping_integrated.csv` | 2,154 | Income + Village Mapping |

---

# 11. Integration Results Summary

| Integration | Total Rows | Matched | Ambiguous | Unmatched | Match Rate |
|---|---:|---:|---:|---:|---:|
| Flood + Mapping | 4,754 | 4,721 | - | 33 | 99.31% |
| Income + Mapping | 2,154 | 1,448 | 28 | 678 | 67.22% |

หมายเหตุ:
- Flood ใช้ `village_code` เป็น Join Key
- Income ใช้ Composite Key จาก District, Subdistrict และ Area
- Flood แสดงสถานะ `matched` และ `unmatched`
- Income แสดงสถานะ `unique_match`, `ambiguous` และ `unmatched`
- Match Rate ของทั้งสอง Integration ใช้จำนวนแถวที่จับคู่ได้หารด้วยจำนวนแถวต้นทาง
- ผลลัพธ์ทั้งสองชุดรักษาจำนวนแถวต้นทางไว้ครบถ้วน

---

# 12. Design Decisions and Rationale

สรุปการตัดสินใจสำคัญในงาน Transformation และ Integration

| Decision | Reason |
|---|---|
| เก็บรหัสพื้นที่เป็น String | ป้องกันเลขศูนย์ด้านหน้าหายและรักษา Identifier |
| ใช้ Left Join | รักษาข้อมูลต้นทางให้ครบ |
| ใช้ `many_to_one` ใน Flood Integration | ป้องกัน Mapping ซ้ำทำให้จำนวนแถวเพิ่ม |
| ใช้ Composite Key สำหรับ Income | ลดความเสี่ยงจากชื่อหมู่บ้านซ้ำ |
| เก็บข้อความในวงเล็บของชื่อพื้นที่ | ป้องกันการรวมหมู่บ้านคนละหมู่เป็น Key เดียวกัน |
| ไม่แก้ชื่อสะกดอัตโนมัติ | ป้องกัน False Match |
| แยก Ambiguous ออกจาก Unique Match | ไม่เลือกพื้นที่โดยไม่มีหลักฐาน |
| เก็บ Unmatched Records | ป้องกันข้อมูลสูญหาย |
| ไม่แทน Missing ด้วย Zero | รักษาความหมายของข้อมูล |
| เก็บ Duplicate Income Records | ไม่มีหลักฐานเพียงพอให้ลบ |
| เก็บ Road Number เป็น String | ข้อมูลถนนมีตัวอักษรและรูปแบบผสม |
| ไม่ Join Damage โดยตรง | รหัสพื้นที่ยังไม่มีความสัมพันธ์ที่ยืนยันกับ Village Code |
| ไม่ใช้ Quarantine ใน Mapping หลัก | ป้องกันการใช้ข้อมูลที่ยังไม่ผ่านการยืนยัน |

---

# 13. Conclusion

กระบวนการ Transformation และ Integration นี้ได้เตรียมข้อมูลหลักสำหรับการวิเคราะห์ผลกระทบจากอุทกภัยในจังหวัดเชียงใหม่ โดยแปลงข้อมูลจากหลายแหล่งให้อยู่ในรูปแบบที่เหมาะสมและเชื่อมโยงข้อมูลที่สามารถยืนยันความสัมพันธ์ได้

ผลลัพธ์สำคัญ ได้แก่:

1. เตรียม Flood Records ปี 2566 และ 2567 รวม 4,754 Records
2. เตรียม Damage Records จำนวน 866 Records
3. เตรียม Household Income จำนวน 2,154 Records
4. เตรียม Village Mapping จำนวน 2,184 Records
5. เชื่อม Flood กับ Village Mapping ได้ 4,721 Records จากทั้งหมด 4,754 Records
6. เชื่อม Household Income กับ Village Mapping ได้อย่างมีเงื่อนไข 1,448 Records
7. แยก Ambiguous และ Unmatched Records เพื่อป้องกันการจับคู่ผิด
8. สร้าง JSON Reports สำหรับตรวจสอบผลการประมวลผล

หลักการที่ใช้ตลอดกระบวนการคือ **Data Integrity over Forced Matching**

กล่าวคือ ให้ความสำคัญกับความถูกต้องและความน่าเชื่อถือของข้อมูลมากกว่าการทำให้ข้อมูลทุกแถวสามารถจับคู่กันได้

ข้อมูลที่ยังไม่สามารถยืนยันความสัมพันธ์ได้จะถูกเก็บไว้และระบุสถานะอย่างชัดเจน เพื่อให้สามารถตรวจสอบและปรับปรุงได้ในอนาคต โดยไม่ทำให้ข้อมูลต้นฉบับสูญหายหรือเกิดความสัมพันธ์ที่ไม่ถูกต้อง

ข้อมูลที่ผ่านกระบวนการนี้พร้อมสำหรับนำไปใช้ในขั้นตอน Exploratory Data Analysis, Geographic Analysis และการศึกษาความสัมพันธ์ระหว่างลักษณะพื้นที่ ประชากร รายได้ และผลกระทบจากน้ำท่วม โดยต้องคำนึงถึงข้อจำกัดของแต่ละ Dataset ตามที่ระบุไว้ในเอกสารนี้
