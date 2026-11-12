"""รัน Pipeline ส่วน Validation -> Transformation -> Integration ในเครื่อง ด้วยคำสั่งเดียว

ไม่ใช้ AWS: อ่านข้อมูลดิบจาก ingestion/data/ แล้วเขียนผลลัพธ์ที่
  validation/ และ transformation/output/, transformation/reports/

วิธีใช้ (รันจาก root ของโปรเจกต์):
    python run_all.py              # รันทุกขั้น แสดงเฉพาะสถานะ
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

# ลำดับสำคัญ: integrate_data.py ต้องรันหลัง create_features.py และ transform_nso_income.py
STEPS = [
    "prepare_local_data.py",
    "ingestion/validate_data.py",
    "transformation/scripts/clean_data.py",
    "transformation/scripts/standardize.py",
    "transformation/scripts/create_features.py",
    "transformation/scripts/transform_flood_village_stats.py",
    "transformation/scripts/transform_nso_income.py",
    "transformation/scripts/transform_disaster_budget.py",
    "transformation/scripts/transform_flood_affected_households.py",
    "transformation/scripts/transform_affected_households_summary.py",
    "transformation/scripts/integrate_data.py",
]

# ไฟล์ผลลัพธ์ -> จำนวนแถวที่คาดหวัง (ตรงกับ transformation/README.md)
EXPECTED_ROWS = {
    "geographic_data_features.csv": 1772,
    "flood_village_stats_transformed.csv": 57024,
    "nso_household_income_transformed.csv": 15400,
    "disaster_budget_2564_transformed.csv": 76,
    "flood_affected_households_transformed.csv": 144,
    "affected_households_summary_transformed.csv": 48,
    "geographic_nso_integrated.csv": 10,
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
        rows = len(pd.read_csv(path))
        status = "OK" if rows == expected else "FAIL"
        all_ok &= rows == expected
        print(f"  [{status}] {name}: {rows:,} แถว (คาดหวัง {expected:,})")
    return all_ok


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--verbose", action="store_true", help="แสดงข้อความของแต่ละสคริปต์")
    args = parser.parse_args()

    for step in STEPS:
        if not run_step(step, args.verbose):
            print(f"\nหยุดที่ขั้น {step} กรุณาแก้ปัญหาตามข้อความด้านบนแล้วรันใหม่")
            sys.exit(1)

    if not check_outputs():
        print("\nจำนวนแถวไม่ตรงกับที่คาดหวัง")
        sys.exit(1)
    print("\nเสร็จสมบูรณ์: ทุกขั้นตอนผ่าน และจำนวนแถวตรงกับที่ทีมรายงานไว้")


if __name__ == "__main__":
    main()
