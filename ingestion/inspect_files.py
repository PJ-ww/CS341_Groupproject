"""ตรวจไฟล์ใน ingestion/data/: encoding, หัวตาราง, จำนวนแถว, ชีตของ xlsx"""
import csv
from pathlib import Path

import openpyxl

DATA_DIR = Path(__file__).parent / "data"


def detect_encoding(path):
    for enc in ("utf-8-sig", "cp874"):
        try:
            with open(path, encoding=enc) as f:
                f.read()
            return enc
        except UnicodeDecodeError:
            continue
    return "unknown"


def inspect_csv(path):
    enc = detect_encoding(path)
    print(f"encoding: {enc}")
    with open(path, encoding=enc if enc != "unknown" else "utf-8", errors="replace") as f:
        rows = list(csv.reader(f))
    print(f"rows (รวมหัวตาราง): {len(rows)} | cols: {len(rows[0]) if rows else 0}")
    for r in rows[:4]:
        print(r)


def inspect_xlsx(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    for ws in wb.worksheets:
        print(f"--- sheet '{ws.title}' rows={ws.max_row} cols={ws.max_column}")
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            print(row[:12])
            if i >= 3:
                break


for p in sorted(DATA_DIR.iterdir()):
    if p.suffix.lower() not in (".csv", ".xlsx"):
        continue
    print(f"\n{'=' * 70}\n{p.name}  ({p.stat().st_size / 1024:.1f} KB)")
    if p.suffix.lower() == ".csv":
        inspect_csv(p)
    else:
        inspect_xlsx(p)