# Orchestration: Deploy Glue/Athena, Lambda และ Step Functions

เอกสารนี้อธิบายการสร้างส่วน AWS ทั้งหมดที่ pipeline ต้องใช้ ตั้งแต่ต้น บน AWS Account ใดก็ได้ ทั้งของทีมเองหรือของผู้ตรวจ

```text
S3 raw/  ->  CheckBatch -> ValidateBatch -> (QuarantineBatch | TransformBatch) -> VerifyBatch
                                                                 |                  |
                                                       S3 processed/<table>/   Athena COUNT(*) ทุกตาราง
```

`VerifyBatch` นับแถวผ่าน Athena ในฐานข้อมูล `flood_recovery_db` จึงต้องสร้างตารางในขั้นที่ 3 ก่อนรัน state machine ครั้งแรก

คำสั่งด้านล่างเขียนสำหรับ Git Bash / macOS / Linux และรันจาก root ของ repo ทั้งหมด

## 0. ตัวแปรที่ใช้

```bash
export AWS_PROFILE=cs341-team        # หรือ profile ของ account ตัวเอง
export AWS_REGION=us-east-1
export BUCKET=cs341-flood-recovery   # ถ้าใช้ account อื่น ต้องตั้งชื่อใหม่ (ชื่อ bucket ซ้ำกันทั่วโลกไม่ได้)
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
```

ถ้าเปลี่ยนชื่อ bucket ต้องแก้ 3 ที่ให้ตรงกัน:

1. `BUCKET` ใน [`ingestion/config.py`](../ingestion/config.py)
2. `LOCATION` ทุกตารางใน [`sql/setup/01_create_tables.sql`](../sql/setup/01_create_tables.sql)
3. ค่า `"bucket"` ใน input ตอนสั่งรัน state machine (ขั้นที่ 6)

## 1. สร้าง S3 bucket และอัปโหลดข้อมูลดิบ

ต้องมีไฟล์ดิบทั้ง 8 ไฟล์ใน `ingestion/data/` ก่อน ดูวิธีโหลดไฟล์ได้ใน [`ingestion/README.md`](../ingestion/README.md) (หัวข้อ 6 หรือ 6B)

```bash
aws s3 mb s3://$BUCKET --region $AWS_REGION      # ข้ามได้ถ้ามี bucket อยู่แล้ว
python ingestion/ingest.py                         # อัปโหลดไป raw/... ตาม config.py และเขียน manifest
aws s3 ls s3://$BUCKET/raw/ --recursive
```

## 2. (ทางเลือก) อัปโหลดผลลัพธ์ที่ commit ไว้แล้วไป processed/

ถ้าต้องการ query ใน Athena ทันทีโดยยังไม่ deploy Lambda ให้อัปโหลดผลลัพธ์ใน `transformation/output/` ขึ้นไปเอง แต่ถ้าจะรัน state machine ข้ามขั้นนี้ได้ เพราะ `TransformBatch` อัปโหลดให้

```bash
OUT=transformation/output
aws s3 cp $OUT/geographic_data_features.csv                       s3://$BUCKET/processed/geographic/
aws s3 cp $OUT/flood_village_stats_transformed.parquet            s3://$BUCKET/processed/flood_village_stats/
aws s3 cp $OUT/nso_household_income_transformed.parquet           s3://$BUCKET/processed/nso_income/
aws s3 cp $OUT/disaster_budget_2564_transformed.parquet           s3://$BUCKET/processed/disaster_budget/
aws s3 cp $OUT/flood_affected_households_transformed.parquet      s3://$BUCKET/processed/flood_affected_households/
aws s3 cp $OUT/affected_households_summary_transformed.parquet    s3://$BUCKET/processed/affected_households_summary/
aws s3 cp $OUT/geographic_nso_integrated.parquet                  s3://$BUCKET/processed/geographic_nso_integrated/
```

แต่ละ prefix ต้องมีไฟล์เพียงไฟล์เดียว เพราะ Athena อ่านทุกไฟล์ใน LOCATION ถ้ามีไฟล์อื่นปนอยู่ จำนวนแถวจะไม่ตรง

## 3. สร้าง Glue Data Catalog / ตาราง Athena

**วิธีที่ 1: DDL (แนะนำ เพราะ schema คงที่)**

1. เปิด Athena console ที่ region `us-east-1` ไปที่ Settings แล้วตั้ง Query result location เป็น `s3://<BUCKET>/athena-results/`
2. รัน statement ใน [`sql/setup/01_create_tables.sql`](../sql/setup/01_create_tables.sql) ทีละ statement (`CREATE DATABASE` แล้วตามด้วย `CREATE EXTERNAL TABLE` ทั้ง 7 ตาราง)
3. รัน query ท้ายไฟล์ จำนวนแถวต้องได้ `1772 / 57024 / 15400 / 76 / 144 / 48 / 10`

หรือรันจาก CLI ทีละ statement:

```bash
aws athena start-query-execution \
  --query-string "CREATE DATABASE IF NOT EXISTS flood_recovery_db" \
  --result-configuration OutputLocation=s3://$BUCKET/athena-results/
```

**วิธีที่ 2: Glue Crawler (วิธีที่ทีมใช้ตอนพัฒนา)**

ต้องมีไฟล์ใน `processed/` แล้ว (ทำขั้นที่ 2 ก่อน หรือรัน state machine ครั้งแรกให้ผ่าน TransformBatch)

```bash
aws glue create-database --database-input Name=flood_recovery_db

# role ของ crawler ต้องมี AWSGlueServiceRole + สิทธิ์อ่าน s3://$BUCKET/processed/*
aws glue create-crawler --name cs341-processed-crawler \
  --role arn:aws:iam::$ACCOUNT_ID:role/<GLUE_CRAWLER_ROLE> \
  --database-name flood_recovery_db \
  --targets "{\"S3Targets\":[
    {\"Path\":\"s3://$BUCKET/processed/geographic/\"},
    {\"Path\":\"s3://$BUCKET/processed/flood_village_stats/\"},
    {\"Path\":\"s3://$BUCKET/processed/nso_income/\"},
    {\"Path\":\"s3://$BUCKET/processed/disaster_budget/\"},
    {\"Path\":\"s3://$BUCKET/processed/flood_affected_households/\"},
    {\"Path\":\"s3://$BUCKET/processed/affected_households_summary/\"},
    {\"Path\":\"s3://$BUCKET/processed/geographic_nso_integrated/\"}]}"

aws glue start-crawler --name cs341-processed-crawler
aws glue get-tables --database-name flood_recovery_db --query "TableList[].Name"
```

ชื่อตารางที่ crawler สร้างต้องตรงกับชื่อโฟลเดอร์ทั้ง 7 ชื่อข้างบน ถ้าไม่ตรง (เช่นมี suffix) ให้ใช้วิธีที่ 1 แทน

## 4. สร้าง IAM roles

**Lambda role** (`cs341-lambda-role`)

```bash
aws iam create-role --role-name cs341-lambda-role --assume-role-policy-document '{
  "Version":"2012-10-17",
  "Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}'

aws iam attach-role-policy --role-name cs341-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam attach-role-policy --role-name cs341-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonAthenaFullAccess   # Athena + Glue Catalog สำหรับ VerifyBatch

aws iam put-role-policy --role-name cs341-lambda-role --policy-name cs341-s3 --policy-document "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[
    {\"Effect\":\"Allow\",\"Action\":[\"s3:ListBucket\"],\"Resource\":\"arn:aws:s3:::$BUCKET\"},
    {\"Effect\":\"Allow\",\"Action\":[\"s3:GetObject\",\"s3:PutObject\"],\"Resource\":\"arn:aws:s3:::$BUCKET/*\"}]}"
```

**Step Functions role** (`cs341-sfn-role`)

```bash
aws iam create-role --role-name cs341-sfn-role --assume-role-policy-document '{
  "Version":"2012-10-17",
  "Statement":[{"Effect":"Allow","Principal":{"Service":"states.amazonaws.com"},"Action":"sts:AssumeRole"}]}'

aws iam put-role-policy --role-name cs341-sfn-role --policy-name invoke-cs341-lambdas --policy-document "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[{\"Effect\":\"Allow\",\"Action\":\"lambda:InvokeFunction\",
    \"Resource\":\"arn:aws:lambda:$AWS_REGION:$ACCOUNT_ID:function:cs341-*\"}]}"
```

## 5. Build และ deploy Lambda ทั้ง 5 ตัว

สคริปต์ transformation ต้องใช้ `pandas`, `pyarrow` และ `openpyxl` ซึ่งไม่มีใน Lambda runtime จึงต้องแนบ AWS managed layer **AWS SDK for pandas** (`AWSSDKPandas-Python312`) ที่มีทั้ง 3 ตัว ดู ARN ล่าสุดของ region ได้ที่ <https://aws-sdk-pandas.readthedocs.io/en/stable/layers.html>

```bash
python orchestration/build_package.py      # สร้าง orchestration/dist/cs341_pipeline.zip

ROLE_ARN=arn:aws:iam::$ACCOUNT_ID:role/cs341-lambda-role
LAYER_ARN=arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python312:<VERSION>   # ใส่เลข version จากลิงก์ด้านบน

for pair in check-batch:check_batch validate-batch:validate_batch quarantine-batch:quarantine_batch \
            transform-batch:transform_batch verify-batch:verify_batch; do
  name=cs341-${pair%%:*}; handler=lambda_handlers.${pair##*:}
  aws lambda create-function --function-name $name \
    --runtime python3.12 --handler $handler --role $ROLE_ARN \
    --zip-file fileb://orchestration/dist/cs341_pipeline.zip \
    --layers $LAYER_ARN --timeout 900 --memory-size 2048 \
    --environment "Variables={BUCKET=$BUCKET,ATHENA_DATABASE=flood_recovery_db}"
done
```

ถ้า role เพิ่งสร้างแล้วเจอ error `The role defined for the function cannot be assumed by Lambda` ให้รอสัก 10-20 วินาทีแล้วรันใหม่

หลังแก้โค้ด ให้ build ใหม่แล้วอัปเดตทุกฟังก์ชัน:

```bash
python orchestration/build_package.py
for f in check validate quarantine transform verify; do
  aws lambda update-function-code --function-name cs341-$f-batch \
    --zip-file fileb://orchestration/dist/cs341_pipeline.zip
done
```

## 6. สร้างและรัน Step Functions

```bash
aws stepfunctions create-state-machine --name cs341-pipeline \
  --definition file://orchestration/state_machine.asl.json \
  --role-arn arn:aws:iam::$ACCOUNT_ID:role/cs341-sfn-role

SM_ARN=arn:aws:states:$AWS_REGION:$ACCOUNT_ID:stateMachine:cs341-pipeline
aws stepfunctions start-execution --state-machine-arn $SM_ARN \
  --input "{\"bucket\":\"$BUCKET\",\"batch_id\":\"2026-11\"}"
```

ดูผลได้ที่ Step Functions console หรือ `aws stepfunctions list-executions --state-machine-arn $SM_ARN`

**ผลที่ควรได้**

| ผลลัพธ์ | ตำแหน่งใน S3 |
|---|---|
| รายงาน validation และไฟล์ cleaned/quarantine | `validation/batch_id=<id>/` |
| ข้อมูลที่แปลงแล้ว 7 ชุด | `processed/<table>/` |
| รายงาน transformation | `reports/batch_id=<id>/` |
| marker ว่ารัน batch นี้สำเร็จแล้ว (ใช้ใน CheckBatch) | `processed/_success/batch_id=<id>/_SUCCESS.json` |
| ไฟล์ของ batch ที่ไม่ผ่าน validation | `quarantine/batch_id=<id>/` |

รัน `batch_id` เดิมซ้ำ state machine จะหยุดที่ `Stop` ทันที (idempotent) ถ้าต้องการรันใหม่ให้ใช้ `batch_id` ใหม่ หรือลบ `_SUCCESS.json` ของ batch นั้น

## 7. ลบ resource หลังทดลอง (ไม่บังคับ)

```bash
aws stepfunctions delete-state-machine --state-machine-arn $SM_ARN
for f in check validate quarantine transform verify; do aws lambda delete-function --function-name cs341-$f-batch; done
aws glue delete-database --name flood_recovery_db
```
