# 06 — Data Storage, Data Model & Query (คนที่ 4)
 
## 1. หน้าที่ของชั้นนี้
 
ชั้น Transformation ส่งออกเป็น CSV 8 ไฟล์ ซึ่งยังไม่เหมาะกับการ Query ซ้ำ ๆ บน Athena เพราะ
(1) CSV ไม่มีชนิดข้อมูล รหัสพื้นที่บางไฟล์กลายเป็นทศนิยม เช่น `502003.0`
(2) Athena ต้องอ่านทั้งไฟล์ทุกครั้ง และ
(3) ไฟล์ integrated คัดลอกคุณลักษณะหมู่บ้านซ้ำไปทุกแถว
 
ชั้นนี้จึงสร้าง **Curated Zone** คือ Parquet ที่กำหนดชนิดข้อมูลชัดเจน แบ่ง partition และลงทะเบียนใน Glue Data Catalog เพื่อให้ Query ตอบ Q1–Q3 ได้
 
```text
transformation/output/*.csv ──build_curated.py──▶ storage/curated/*.parquet ──upload_to_s3.py──▶ s3://cs341-flood-recovery/curated/
                                                                                                     │
                                       sql/curated/01_create_curated_tables.sql (Glue Catalog) ◀─────┘
                                       sql/curated/02_create_views.sql  →  sql/curated/queries/*.sql (Athena)
```
 
## 2. Data Model (Star Schema)
 
```mermaid
erDiagram
    dim_village ||--o{ fact_flood_report : "village_code"
    dim_village ||--o{ fact_household_income : "village_code (unique_match เท่านั้น)"
    dim_village }o--o{ fact_disaster_damage : "district_code"
 
    dim_village {
        string village_code PK
        string district_code
        string subdistrict_code
        double latitude
        bigint population_total
        bigint households
        int river_flag
        int mountain_flag
    }
    fact_flood_report {
        int source_year PK "partition"
        string source_record_id PK
        string village_code FK
        date disaster_date
        bigint affected_households
    }
    fact_disaster_damage {
        string source_record_id PK
        int source_year "partition"
        string district_code FK
        bigint affected_households
        bigint houses_damaged
    }
    fact_household_income {
        string income_record_id PK
        string village_code FK "NULL ถ้า ambiguous/unmatched"
        bigint avg_household_income_baht_per_year
        string mapping_match_status
    }
```
 
| ตาราง | Grain (1 แถว =) | แถว | Partition | ที่มา |
|---|---|---:|---|---|
| `dim_village` | 1 หมู่บ้านในเชียงใหม่ | 2,184 | – | `village_mapping_transformed.csv` |
| `fact_flood_report` | 1 หมู่บ้านใน 1 เหตุการณ์อุทกภัย | 4,754 | `source_year` (2566, 2567) | `flood_chiangmai_combined.csv` |
| `fact_disaster_damage` | 1 รายการความเสียหาย ต่อวันที่เกิดเหตุ | 866 | `source_year` (2563–2567) | `chiangmai_damage_transformed.csv` |
| `fact_household_income` | 1 พื้นที่ในข้อมูลรายได้ (ไม่มีปี) | 2,154 | – | `household_income_mapping_integrated.csv` |
 
View สำหรับใช้งาน (Serving):
- `v_flood_report_village` คือรายงานน้ำท่วม + คุณลักษณะหมู่บ้าน (LEFT JOIN และมีธง `village_found`)
- `v_village_profile` คือ 1 แถวต่อหมู่บ้าน มีจำนวนครั้งที่ถูกรายงานน้ำท่วมแยกตามปี ภูมิศาสตร์ ประชากร และรายได้
## 3. Design Decisions & Trade-offs
 
| # | การตัดสินใจ | เหตุผล | Trade-off |
|---|---|---|---|
| D1 | **Star schema**: แยก `dim_village` ออกจาก fact และ JOIN ตอน query แทนการใช้ไฟล์ integrated ที่ copy คอลัมน์หมู่บ้านทุกแถว | คุณลักษณะหมู่บ้านมีที่เก็บที่เดียว แก้ที่เดียวแล้วทุก query เปลี่ยนตาม และ fact เล็กลง | ทุก query ต้อง JOIN แต่ dim มีแค่ 2,184 แถว จึงแทบไม่มีต้นทุน |
| D2 | **Parquet (Snappy)** แทน CSV | เป็น columnar format จึงอ่านเฉพาะคอลัมน์ที่ใช้ เก็บชนิดข้อมูลในไฟล์ และขนาดลดลงมาก (flood 1.83 MB → 0.14 MB, dim 1.04 MB → 0.24 MB) | ต้องเปิดผ่านเครื่องมือ ไม่ใช่ text editor |
| D3 | **Partition ด้วย `source_year` เท่านั้น** (ไม่แบ่งซ้อนด้วยอำเภอ) | Q1 กรอง/เปรียบเทียบตามปีเป็นหลัก Athena จึง prune ได้ ถ้าแบ่ง ปี × 25 อำเภอ จะได้ไฟล์ละไม่กี่สิบแถว (small files problem) | damage แบ่ง 5 ปี ได้ไฟล์ละ 120–300 แถว ทำให้ Parquet (68 KB) ใหญ่กว่า CSV (68 KB) เล็กน้อยจาก overhead ของ footer ซึ่งยอมรับได้เพื่อให้โครงสร้างสอดคล้องกับ flood และรองรับปีใหม่ |
| D4 | `dim_village` และ `fact_household_income` **ไม่ partition** | dim ไม่มีมิติเวลาและเล็ก ส่วนข้อมูลรายได้ไม่มีปีกำกับ | – |
| D5 | **Partition projection** แทน `MSCK REPAIR TABLE` | ไม่ต้องลงทะเบียน partition เองทุกครั้งที่มีปีใหม่ ลดขั้นตอน manual ใน pipeline | ต้องขยาย `projection.source_year.range` ใน `generate_ddl.py` เมื่อมีปีใหม่ |
| D6 | **Schema กำหนดใน `storage/schema.py` ที่เดียว** แล้ว generate DDL | ไฟล์ Parquet กับตารางใน Glue Catalog ตรงกันเสมอ (Athena error `HIVE_BAD_DATA` ถ้าชนิดไม่ตรง) | ต้องรัน `generate_ddl.py` ใหม่เมื่อแก้ schema |
| D7 | รหัสพื้นที่เก็บเป็น **string ความยาวคงที่** (`village_code` 8 หลัก, `subdistrict_code` 6 หลัก) | ป้องกัน `.0` และเลข 0 นำหน้าหาย ซึ่งทำให้ JOIN พลาดแบบเงียบ ๆ และ dim เดิมใช้ตำบล 8 หลัก (`50010100`) ขณะที่ flood ใช้ 6 หลัก จึงปรับให้เป็นมาตรฐานเดียว | – |
| D8 | **Parquet + Hive table** เป็นหลัก ส่วน Iceberg เป็น optional (`03_iceberg_optional.sql`) | ข้อมูลเล็ก (~10k แถว) โหลดแบบ batch full refresh และไม่มี row-level update/delete จึงยังไม่ต้องใช้ ACID/MERGE | Hive table ไม่เก็บประวัติ batch ถ้าทีมต้องการแก้ปัญหา `processed/` ถูกเขียนทับ (Issue #15) Iceberg snapshot + time travel ช่วยได้ |
| D9 | ไม่ทิ้งแถวที่จับคู่ไม่ได้ | Flood 33 แถวที่ไม่พบใน dim และรายได้ ambiguous/unmatched ยังอยู่ใน fact โดย view ติดธงไว้ ผลรวมจึงไม่เพี้ยน | การวิเคราะห์ที่ต้องใช้คุณลักษณะหมู่บ้านจะใช้ได้เฉพาะแถวที่จับคู่ได้ |
 
## 4. Data Quality ของชั้น Curated (ผลรันจริง)
 
`build_curated.py` หยุดทำงานทันทีถ้าค่าใดแปลงชนิดไม่ได้ (ไม่แปลงเป็น NULL แบบเงียบ ๆ) และตรวจจำนวนแถวกับ primary key ดู `storage/reports/curated_build_report.json`
 
| Check (`sql/curated/data_quality/`) | ผล |
|---|---|
| dq_01 จำนวนแถว = ต้นทาง ทุกตาราง/partition | ผ่าน (2,184 / 1,198+3,556 / 866 / 2,154) |
| dq_02 Primary key ไม่ซ้ำ ไม่ว่าง | ผ่าน (0 ซ้ำ ทุกตาราง) |
| dq_03 Flood → dim_village | 4,721/4,754 = **99.31%** (ตรงกับรายงานคนที่ 3) |
| dq_03 Income → dim_village | 1,448/2,154 = **67.22%** (ตรงกับรายงานคนที่ 3) |
| dq_03 Damage → อำเภอใน dim | 866/866 = 100% |
| dq_05 damage ที่ตัวเลขเป็น 0 ทุกช่อง | 2563–2566 มี 2–10% แต่ปี 2567 มี 54/182 = **29.7%** (เช่น อมก๋อย 12 แถว) ตัวเลขรวมปี 2567 จึงต่ำกว่าความจริง |
| dq_04 ความครบของตัวชี้วัด | `affected_households` ใน flood มีค่าแค่ 15.9% (2566) และ 6.1% (2567) ส่วน damage ครบ 100% แต่ `partially_damaged_houses` ปี 2566–2567 ว่างทั้งหมด |
 
ผล dq_04 เป็นเหตุผลที่ Q1 ใช้ **จำนวนหมู่บ้านที่ถูกรายงาน** เป็นตัวชี้วัดหลักจากข้อมูล flood และใช้ตัวเลขผู้ได้รับผลกระทบจากข้อมูล damage แทน
 
## 5. Query ที่ตอบคำถาม (รันบนข้อมูลจริงแล้ว ผลอยู่ใน `storage/query_results/`)
 
| คำถาม | Query | สิ่งที่ได้ |
|---|---|---|
| Q1 พื้นที่ใดได้รับผลกระทบมากที่สุด/เปลี่ยนอย่างไรรายปี | `q1_1` หมู่บ้านที่ถูกรายงานรายอำเภอ 2566 vs 2567, `q1_2` แนวโน้มความเสียหาย 2563–2567 (10 อำเภอแรก), `q1_3` หมู่บ้านที่ถูกรายงานซ้ำทั้งสองปี | แม่แจ่ม จอมทอง อมก๋อย ถูกรายงานสูงทั้งสองปี ส่วนเมืองเชียงใหม่ สารภี หางดง สันป่าตอง เพิ่มขึ้นมากในปี 2567 |
| Q2 ภูมิศาสตร์/ประชากรสัมพันธ์กับผลกระทบหรือไม่ | `q2_1` % หมู่บ้านที่ถูกรายงาน แยกตาม flag ภูมิศาสตร์, `q2_2` แยกตาม quartile ประชากร/รายได้ | หมู่บ้านติดแม่น้ำ 80.3% เทียบกับ 75.1% และติดภูเขา 86.8% เทียบกับ 77.7% ความต่างไม่มาก เพราะหมู่บ้าน 78.7% ถูกรายงานอย่างน้อย 1 ครั้ง (เป็นความสัมพันธ์เชิงพรรณนา ไม่ใช่เหตุผล) |
| Q3 จัดลำดับพื้นที่ช่วยเหลือ | `q3_1` คะแนนรายหมู่บ้าน (0.5 ความถี่ + 0.3 ครัวเรือน + 0.2 รายได้ต่ำ), `q3_2` สรุปรายอำเภอ | ได้รายการลำดับที่ตรวจสอบย้อนกลับได้ โดยน้ำหนักเป็นสมมติฐานที่ทีมต้องตกลงและระบุในรายงาน |
 
## 6. หลักฐานการรันบน AWS (S3 + Athena)

### 6.1 Curated Zone บน S3

`s3://cs341-flood-recovery/curated/` มี 4 ตาราง

![S3 curated layout](evidence/s3_curated_layout.png)

`fact_flood_report` แบ่ง partition ตาม `source_year`

![fact_flood_report partitions](evidence/s3_fact_flood_report_partitions.png)

### 6.2 Data Quality checks

**dq_01 จำนวนแถวต่อตาราง/partition**

![dq_01](evidence/athena_dq_01.png)

**dq_02 Primary key ไม่ซ้ำ ไม่ว่าง**

![dq_02](evidence/athena_dq_02.png)

**dq_03 Join coverage**

![dq_03](evidence/athena_dq_03.png)

**dq_04 ความครบของตัวชี้วัด**

![dq_04](evidence/athena_dq_04.png)

**dq_05 damage ที่ตัวเลขเป็น 0 ทุกช่อง**

![dq_05](evidence/athena_dq_05.png)

### 6.3 Query ตอบคำถาม

**q1_1 หมู่บ้านที่ถูกรายงานรายอำเภอ 2566 vs 2567**

![q1_1](evidence/athena_q1_1.png)

**q1_2 แนวโน้มความเสียหาย 2563–2567 (10 อำเภอแรก)**

![q1_2](evidence/athena_q1_2.png)

**q1_3 หมู่บ้านที่ถูกรายงานซ้ำทั้งสองปี**

![q1_3](evidence/athena_q1_3.png)

**q2_1 ภูมิศาสตร์กับการถูกรายงานน้ำท่วม**

![q2_1](evidence/athena_q2_1.png)

**q2_2 Quartile ประชากร/รายได้กับการถูกรายงานน้ำท่วม**

![q2_2](evidence/athena_q2_2.png)

**q3_1 คะแนนจัดลำดับช่วยเหลือรายหมู่บ้าน**

![q3_1](evidence/athena_q3_1.png)

**q3_2 สรุปลำดับช่วยเหลือรายอำเภอ**

![q3_2](evidence/athena_q3_2.png)

### 6.4 Partition pruning

Query เดียวกันบน `fact_flood_report` เมื่อไม่กรองปี Athena สแกน **17.87 KB** แต่เมื่อกรอง `WHERE source_year = 2566` สแกนเหลือ **5.23 KB** (ลดลงประมาณ 70%) แสดงว่า Athena อ่านเฉพาะ partition ที่ต้องใช้

| ไม่กรองปี | `source_year = 2566` |
|---|---|
| ![pruning all](evidence/athena_pruning_all.png) | ![pruning 2566](evidence/athena_pruning_2566.png) |

## 7. ข้อจำกัด
 
- จำนวนรายงานน้ำท่วมสะท้อน **การถูกรายงาน** ไม่ใช่ความรุนแรงจริง ปี 2566 อาจรายงานไม่ครบเท่าปี 2567 (เช่น เมืองเชียงใหม่ 0 หมู่บ้านในปี 2566)
- ข้อมูลรายได้ไม่มีปี และจับคู่หมู่บ้านได้ 67% ดังนั้นองค์ประกอบรายได้ใน Q3 จึงขาดไปประมาณ 1/3 ของหมู่บ้าน (ใช้ค่ากลาง 0.5 และติดธง `income_available`)
- ข้อมูล damage ปี 2567 มี 29.7% ของแถวที่ตัวเลขเป็น 0 ทุกช่อง จึงไม่ควรตีความว่าความเสียหายปี 2567 ลดลง
- ข้อมูล damage มี `subdistrict_id` และ `village_id` เป็นลำดับเลข ไม่ใช่รหัสมาตรฐาน ตอนนี้จึงเชื่อมได้แค่ระดับอำเภอ จากการทดลองสร้างรหัส `district_code + ตำบล 2 หลัก + หมู่ 2 หลัก` ตรงกับ dim ได้ 622/866 แถว (72%) แต่ยังไม่ได้ยืนยันว่าเลขชุดนี้คือรหัสเดียวกันจริง จึงยังไม่นำมาใช้
## 8. วิธีรัน
 
ดู [`storage/README.md`](../storage/README.md)
 