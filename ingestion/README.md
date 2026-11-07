# Ingestion and validation

- `inspect_files.py` แสดงหัวตารางและตัวอย่างข้อมูลจาก CSV/XLSX (ต้องติดตั้ง `openpyxl`)
- `validate_data.py` ตรวจเงื่อนไขคุณภาพพื้นฐานจากไฟล์ใน `data/` โดยไม่แก้ raw และแยกผลไว้ที่ root ของ repo ใน `validation/reports/`, `validation/cleaned/` และ `validation/quarantine/`
- ดูวิธีตรวจ กฎ และผลล่าสุดใน [`docs/04-data-validation.md`](../docs/04-data-validation.md)

รัน validator จาก root ของ repo:

```powershell
python ingestion/validate_data.py
```
