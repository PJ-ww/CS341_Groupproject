"""จัดโครงสร้างโฟลเดอร์ raw ให้สคริปต์ transformation รันในเครื่องได้โดยไม่ต้องใช้ AWS

สคริปต์ transformation บางตัวอ่านไฟล์จาก ingestion/data/<s3_prefix>/<s3_name> (เช่น ingestion/data/raw/nso/...)
(เลียนแบบโครงสร้างบน S3) สคริปต์นี้คัดลอกไฟล์จาก ingestion/data/ ไปวางตามโครงสร้างนั้น
โดยอ่านการแมปจาก ingestion/config.py (ไม่แก้ไขไฟล์ต้นฉบับ)

วิธีใช้ (รันจาก root ของโปรเจกต์):  python prepare_local_data.py
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "ingestion"))
from config import FILES  # noqa: E402

DATA = ROOT / "ingestion" / "data"
ok = True
for item in FILES:
    src = DATA / item["local_file"]
    dst = DATA / item["s3_prefix"] / item["s3_name"]
    if not src.exists():
        print(f"[MISSING] {src}")
        ok = False
        continue
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"[OK] {item['local_file']} -> {dst.relative_to(ROOT)}")

sys.exit(0 if ok else 1)
