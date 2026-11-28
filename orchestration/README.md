# Orchestration: Deploy Lambda, Step Functions และ Glue/Athena

เอกสารนี้อธิบายการสร้างส่วน AWS ทั้งหมดที่ pipeline ต้องใช้ ตั้งแต่ต้น บน AWS Account ใดก็ได้ ทั้งของทีมเองหรือของผู้ตรวจ แผนภาพรวมอยู่ที่ [`docs/architecture_diagram.png`](../docs/architecture_diagram.png)

```text
S3 raw/ (5 ไฟล์) -> CheckBatch -> ValidateBatch -> (QuarantineBatch | TransformBatch) -> VerifyBatch
                                       |                  |                 |               |
                            validation/batch_id=<id>/  quarantine/   transformation/output/  นับแถว CSV เทียบ DATASETS
                                                                     transformation/reports/  แล้วเขียน _SUCCESS.json

หลัง batch สำเร็จ (ยังรันด้วยมือ): build_curated.py -> upload_to_s3.py -> S3 curated/ -> Glue Data Catalog -> Athena
```

`VerifyBatch` ดาวน์โหลด CSV 8 ไฟล์จาก `transformation/output/` มานับแถวเทียบกับ `DATASETS` ใน [`lambda_handlers.py`](lambda_handlers.py) และตรวจว่ามีรายงานครบ 6 ไฟล์ จึงไม่ต้องสร้างตาราง Athena ก่อนรัน state machine

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
2. `BUCKET` ใน [`storage/schema.py`](../storage/schema.py) แล้วรัน `python storage/generate_ddl.py` เพื่อสร้าง `LOCATION` ใน [`sql/curated/01_create_curated_tables.sql`](../sql/curated/01_create_curated_tables.sql) ใหม่
3. ค่า `"bucket"` ใน input ตอนสั่งรัน state machine (ขั้นที่ 4)

## 1. สร้าง S3 bucket และอัปโหลดข้อมูลดิบ

ต้องมีไฟล์ดิบทั้ง 5 ไฟล์ใน `ingestion/data/` ก่อน ดูวิธีหาไฟล์ได้ใน [`ingestion/README.md`](../ingestion/README.md) (หัวข้อ 6 หรือ 6B) และที่มาของแต่ละไฟล์ใน [`data_catalog/sources.md`](../data_catalog/sources.md)

```bash
aws s3 mb s3://$BUCKET --region $AWS_REGION      # ข้ามได้ถ้ามี bucket อยู่แล้ว
python ingestion/ingest.py                         # อัปโหลดไป raw/... ตาม config.py และเขียน manifest
aws s3 ls s3://$BUCKET/raw/ --recursive
```

## 2. สร้าง IAM roles

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

## 3. Build และ deploy Lambda ทั้ง 5 ตัว

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

## 4. สร้างและรัน Step Functions

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
| ข้อมูลที่แปลงแล้ว 8 ไฟล์ (CSV) | `transformation/output/` |
| รายงาน transformation 6 ไฟล์ | `transformation/reports/` |
| marker ว่ารัน batch นี้สำเร็จแล้ว พร้อมจำนวนแถว (ใช้ใน CheckBatch) | `transformation/_success/batch_id=<id>/_SUCCESS.json` |
| ไฟล์ของ batch ที่ไม่ผ่าน validation พร้อม `reason.json` | `quarantine/batch_id=<id>/` |

รัน `batch_id` เดิมซ้ำ state machine จะหยุดที่ `Stop` ทันที (idempotent) ถ้าต้องการรันใหม่ให้ใช้ `batch_id` ใหม่ หรือลบ `_SUCCESS.json` ของ batch นั้น

## 5. Curated Zone, Glue Data Catalog และ Athena

หลัง batch สำเร็จ สร้างตารางสำหรับ query (ขั้นนี้ยังไม่ได้เป็น state ใน Step Functions) ก่อนเริ่ม ให้เปิด Athena console ที่ region `us-east-1` ไปที่ Settings แล้วตั้ง Query result location เป็น `s3://<BUCKET>/athena-results/`

```bash
python storage/build_curated.py                                              # transformation/output/ -> Parquet ใน storage/curated/
python storage/upload_to_s3.py                                               # -> s3://$BUCKET/curated/
python storage/run_athena.py --sql sql/curated/01_create_curated_tables.sql  # database flood_recovery_db + 4 ตาราง (partition projection)
python storage/run_athena.py --sql sql/curated/02_create_views.sql           # view 2 ตัว
python storage/run_athena.py --sql sql/curated/data_quality --sql sql/curated/queries --save
```

หรือเปิด Athena Query Editor แล้วรันทีละ statement จากไฟล์เดียวกัน ผู้ใช้ที่รัน `run_athena.py` ต้องมีสิทธิ์ Athena, Glue Catalog และ S3 รายละเอียดอยู่ใน [`storage/README.md`](../storage/README.md) และ [`docs/06-storage-data-model-query.md`](../docs/06-storage-data-model-query.md)

## 6. ลบ resource หลังทดลอง (ไม่บังคับ)

```bash
aws stepfunctions delete-state-machine --state-machine-arn $SM_ARN
for f in check validate quarantine transform verify; do aws lambda delete-function --function-name cs341-$f-batch; done
aws glue delete-database --name flood_recovery_db
```
