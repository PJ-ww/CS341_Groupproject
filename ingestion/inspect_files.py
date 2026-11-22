"""ตรวจไฟล์ใน ingestion/data/: encoding, หัวตาราง, จำนวนแถว, ชีต XLSX และโครงสร้าง JSON."""
import csv
import json
from pathlib import Path

import openpyxl

DATA_DIR = Path(__file__).parent / "data"


def detect_encoding(path):
    for enc in ("utf-8-sig", "cp874"):
        try:
            with path.open(encoding=enc, newline="") as stream:
                stream.read()
            return enc
        except UnicodeDecodeError:
            continue
    return "unknown"


def inspect_csv(path):
    encoding = detect_encoding(path)
    print(f"encoding: {encoding}")
    if encoding == "unknown":
        print("ไม่สามารถระบุ encoding เป็น UTF-8 หรือ cp874 ได้")
        return

    with path.open(encoding=encoding, newline="") as stream:
        rows = list(csv.reader(stream))

    print(f"rows (รวมหัวตาราง): {len(rows)} | cols: {len(rows[0]) if rows else 0}")
    for row in rows[:4]:
        print(row)


def inspect_xlsx(path):
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        for worksheet in workbook.worksheets:
            print(f"--- sheet '{worksheet.title}' rows={worksheet.max_row} cols={worksheet.max_column}")
            for index, row in enumerate(worksheet.iter_rows(values_only=True)):
                print(row[:12])
                if index >= 3:
                    break
    finally:
        workbook.close()


def inspect_json(path):
    with path.open(encoding="utf-8-sig") as stream:
        data = json.load(stream)

    print(f"root type: {type(data).__name__}")
    if isinstance(data, dict):
        print(f"top-level keys ({len(data)}): {list(data.keys())[:30]}")
        # Common GeoJSON / wrapped-record structures
        for key, value in data.items():
            if isinstance(value, list):
                print(f"list field: {key} | records: {len(value)}")
                if value and isinstance(value[0], dict):
                    print(f"first record keys: {list(value[0].keys())[:30]}")
                break
    elif isinstance(data, list):
        print(f"records: {len(data)}")
        if data and isinstance(data[0], dict):
            print(f"first record keys: {list(data[0].keys())[:30]}")
            print(f"first record sample: {data[0]}")
        elif data:
            print(f"first item sample: {data[0]}")


def main():
    if not DATA_DIR.exists():
        raise SystemExit(f"Data directory not found: {DATA_DIR}")

    files = sorted(path for path in DATA_DIR.iterdir() if path.is_file())
    if not files:
        raise SystemExit(f"No files found in {DATA_DIR}")

    for path in files:
        print(f"\n{'=' * 70}\n{path.name} ({path.stat().st_size / 1024:.1f} KB)")
        suffix = path.suffix.lower()
        if suffix == ".csv":
            inspect_csv(path)
        elif suffix == ".xlsx":
            inspect_xlsx(path)
        elif suffix == ".json":
            inspect_json(path)
        else:
            print(f"Unsupported file extension: {suffix}")


if __name__ == "__main__":
    main()
