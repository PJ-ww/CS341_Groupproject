"""รัน Pipeline ส่วน Transformation -> Integration -> Storage -> Query ในเครื่อง ด้วยคำสั่งเดียว

ไม่ใช้ AWS: เริ่มจาก validation/cleaned/ (commit ไว้แล้ว) แล้วเขียนผลลัพธ์ที่
  transformation/output/, transformation/reports/, storage/curated/, storage/query_results/

วิธีใช้ (รันจาก root ของโปรเจกต์):
    python run_all.py              # เริ่มจาก validation/cleaned/ แสดงเฉพาะสถานะ
    python run_all.py --from-raw   # รัน validation จากไฟล์ดิบใน ingestion/data/ ก่อน
    python run_all.py --verbose    # แสดงข้อความที่แต่ละสคริปต์พิมพ์ออกมาด้วย

หยุดทันทีเมื่อมีขั้นใดล้มเหลว (exit code 1) และจบด้วยการตรวจจำนวนแถวของผลลัพธ์
เทียบกับค่าที่ทีมรายงานไว้ใน transformation/README.md
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ต้องมีไฟล์ดิบ 5 ไฟล์ใน ingestion/data/ (ดู ingestion/config.py)
VALIDATION_STEPS = [
    "ingestion/validate_data.py",
]

# ลำดับสำคัญ: integrate_* ต้องรันหลัง transform_* และ build_curated.py ต้องรันหลังสุดของ transformation
STEPS = [
    "transformation/scripts/transform_flood.py",
    "transformation/scripts/transform_damage.py",
    "transformation/scripts/transform_household_income.py",
    "transformation/scripts/transform_village_mapping.py",
    "transformation/scripts/integrate_flood_mapping.py",
    "transformation/scripts/integrate_household_income_mapping.py",
    "storage/build_curated.py",
    "storage/run_local_queries.py",
]

# ไฟล์ผลลัพธ์ -> จำนวนแถวที่คาดหวัง (ตรงกับ transformation/README.md และ docs/06-storage-data-model-query.md)
EXPECTED_ROWS = {
    "flood_2566_transformed.csv": 1198,
    "flood_2567_transformed.csv": 3556,
    "flood_chiangmai_combined.csv": 4754,
    "chiangmai_damage_transformed.csv": 866,
    "household_income_transformed.csv": 2154,
    "village_mapping_transformed.csv": 2184,
    "flood_mapping_integrated.csv": 4754,
    "household_income_mapping_integrated.csv": 2154,
}


def run_step(step, verbose):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    start = time.time()
    proc = subprocess.run(
        [sys.executable, str(ROOT / step)], cwd=ROOT, env=env,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    seconds = time.time() - start
    ok = proc.returncode == 0
    print(f"[{'OK' if ok else 'FAIL'}] {step}  ({seconds:.1f}s)")
    if verbose or not ok:
        for line in (proc.stdout + proc.stderr).rstrip().splitlines():
            print(f"      {line}")
    return ok


def check_outputs():
    import pandas as pd

    print("\nตรวจจำนวนแถวของผลลัพธ์")
    all_ok = True
    for name, expected in EXPECTED_ROWS.items():
        path = ROOT / "transformation" / "output" / name
        if not path.exists():
            print(f"  [FAIL] {name}: ไม่พบไฟล์")
            all_ok = False
            continue
        rows = len(pd.read_csv(path, dtype=str))
        status = "OK" if rows == expected else "FAIL"
        all_ok &= rows == expected
        print(f"  [{status}] {name}: {rows:,} แถว (คาดหวัง {expected:,})")
    return all_ok


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--from-raw", action="store_true",
                        help="รัน validation จากไฟล์ดิบใน ingestion/data/ ก่อน (ค่าเริ่มต้นใช้ validation/cleaned/ ที่ commit ไว้)")
    parser.add_argument("--verbose", action="store_true", help="แสดงข้อความของแต่ละสคริปต์")
    args = parser.parse_args()

    steps = (VALIDATION_STEPS if args.from_raw else []) + STEPS
    for step in steps:
        if not run_step(step, args.verbose):
            print(f"\nหยุดที่ขั้น {step} กรุณาแก้ปัญหาตามข้อความด้านบนแล้วรันใหม่")
            sys.exit(1)

    if not check_outputs():
        print("\nจำนวนแถวไม่ตรงกับที่คาดหวัง")
        sys.exit(1)
    print("\nเสร็จสมบูรณ์: ทุกขั้นตอนผ่าน และจำนวนแถวตรงกับที่ทีมรายงานไว้")


if __name__ == "__main__":
    main()
