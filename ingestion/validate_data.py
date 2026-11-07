"""Run project-specific quality checks on the downloaded raw datasets.

Raw files are read-only inputs. Results are split under validation/ into
reports/, cleaned/, and quarantine/.
The XLSX reader uses Python's standard library so validation does not require
installing a workbook package.
"""
import csv
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
VALIDATION_DIR = Path(__file__).parent.parent / "validation"
REPORT_DIR = VALIDATION_DIR / "reports"
QUARANTINE_DIR = VALIDATION_DIR / "quarantine"
CLEANED_DIR = VALIDATION_DIR / "cleaned"
XLSX_NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def read_csv(path):
    for encoding in ("utf-8-sig", "cp874"):
        try:
            with path.open(encoding=encoding, newline="") as stream:
                rows = list(csv.reader(stream))
            return rows, encoding
        except UnicodeDecodeError:
            continue
    raise ValueError("CSV encoding is neither UTF-8 nor Windows Thai (cp874)")


def column_number(cell_ref):
    letters = re.match(r"[A-Z]+", cell_ref).group(0)
    number = 0
    for letter in letters:
        number = number * 26 + ord(letter) - 64
    return number - 1


def read_xlsx(path):
    """Read worksheet cell values and row numbers from a basic XLSX package."""
    with zipfile.ZipFile(path) as package:
        names = set(package.namelist())
        shared = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(package.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in item.findall(".//m:t", XLSX_NS))
                      for item in root.findall("m:si", XLSX_NS)]
        workbook = ET.fromstring(package.read("xl/workbook.xml"))
        rels = ET.fromstring(package.read("xl/_rels/workbook.xml.rels"))
        targets = {item.attrib["Id"]: item.attrib["Target"] for item in rels}
        result = {}
        for sheet in workbook.findall("m:sheets/m:sheet", XLSX_NS):
            rel_id = sheet.attrib["{" + XLSX_NS["r"] + "}id"]
            target = targets[rel_id].lstrip("/")
            if not target.startswith("xl/"):
                target = "xl/" + target
            root = ET.fromstring(package.read(target))
            rows = []
            for row_node in root.findall(".//m:sheetData/m:row", XLSX_NS):
                row_index = int(row_node.attrib.get("r", len(rows) + 1))
                cells = {}
                for cell in row_node.findall("m:c", XLSX_NS):
                    ref = cell.attrib.get("r", "A1")
                    idx = column_number(ref)
                    value = cell.find("m:v", XLSX_NS)
                    if cell.attrib.get("t") == "inlineStr":
                        text = "".join(t.text or "" for t in cell.findall(".//m:t", XLSX_NS))
                    elif value is None:
                        text = ""
                    else:
                        text = value.text or ""
                        if cell.attrib.get("t") == "s" and text:
                            text = shared[int(text)]
                    cells[idx] = text
                width = max(cells, default=-1) + 1
                rows.append({"row_number": row_index, "values": [cells.get(i, "") for i in range(width)]})
            result[sheet.attrib["name"]] = rows
    return result


def clean(value):
    return str(value or "").strip()


def parse_number(value):
    value = clean(value).replace(",", "")
    if value in ("", "-", "—"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def exact_duplicate_rows(headers, rows):
    """Return later occurrences of literal duplicate records, preserving first."""
    seen = set()
    duplicate_indices = set()
    for i, row in enumerate(rows):
        signature = tuple("" if row.get(h) is None else str(row.get(h)) for h in headers)
        if signature in seen:
            duplicate_indices.add(i)
        else:
            seen.add(signature)
    return duplicate_indices


def validate_table(file_name, headers, raw_rows):
    headers = [clean(h) for h in headers]
    issues = []
    if any(not header for header in headers):
        issues.append("blank column name")
    quarantine = []
    notes = []
    if len(headers) != len(set(headers)):
        issues.append("duplicate column names")
    duplicate_names = [name for name, count in Counter(headers).items() if name and count > 1]
    if duplicate_names:
        issues.append("duplicate column names: " + ", ".join(duplicate_names))

    rows = []
    for row in raw_rows:
        values = list(row["values"])
        reasons = []
        if len(values) != len(headers):
            reasons.append("row width differs from header")
        values = (values + [""] * len(headers))[:len(headers)]
        record = {header: value for header, value in zip(headers, values)}
        rows.append({"row_number": row["row_number"], "data": record, "reasons": reasons})

    if file_name == "Geographic_Data.csv":
        required = ["ปี", "รายการ", "อำเภอ", "ตำบล", "ความเสี่ยง", "เหล่งที่มา"]
        risk_levels = {"เสี่ยงสูงมาก", "เสี่ยงสูง", "เสี่ยงปานกลาง", "เสี่ยงต่ำ", "เสี่ยงต่ำมาก"}
        for row in rows:
            d = row["data"]
            for col in required:
                if not clean(d.get(col)):
                    row["reasons"].append("missing required field: " + col)
            if clean(d.get("ปี")) and not re.fullmatch(r"\d{4}", clean(d["ปี"])):
                row["reasons"].append("ปี is not a four-digit Buddhist Era year")
            if clean(d.get("ความเสี่ยง")) not in risk_levels:
                row["reasons"].append("unknown risk category")
        notes.append("หมู่ที่ว่างได้ เพราะรายการบางแถวเป็นระดับตำบล ไม่ใช่ระดับหมู่บ้าน")
        notes.append("พบชื่อหัวคอลัมน์ 'เหล่งที่มา'; ควรยืนยันกับเจ้าของข้อมูลก่อนเปลี่ยนชื่อ")

    elif file_name == "Number_of Households_Affected_by_Flooding.csv":
        required = ["ปี", "รายการ", "อำเภอ", "ตำบล", "จำนวน", "หน่วย", "ที่มา"]
        for row in rows:
            d = row["data"]
            for col in required:
                if not clean(d.get(col)):
                    row["reasons"].append("missing required field: " + col)
            count = parse_number(d.get("จำนวน"))
            if count is None or count < 0 or not count.is_integer():
                row["reasons"].append("จำนวน must be a non-negative integer")
            if clean(d.get("หน่วย")) != "ครัวเรือน":
                row["reasons"].append("unexpected unit (expected ครัวเรือน)")

    elif file_name == "Salary.csv":
        numeric = ["year", "value"]
        required = ["year", "province", "source_income1", "source_income2", "source_income3",
                    "soc_eco_class1", "soc_eco_class2", "value", "unit", "source"]
        for row in rows:
            d = row["data"]
            for col in required:
                if not clean(d.get(col)):
                    row["reasons"].append("missing required field: " + col)
            for col in numeric:
                value = parse_number(d.get(col))
                if value is None:
                    row["reasons"].append(col + " must be numeric")
        notes.append("ช่อง attribute ว่างได้; ค่า '.00' เป็นค่าศูนย์ตามคำอธิบายใน attribute ไม่ใช่ค่าว่าง")
        notes.append("ค่า value ติดลบรับไว้ เพราะกำไรสุทธิจากธุรกิจ/เกษตรอาจเป็นผลขาดทุนได้")

    elif file_name == "Salary2.csv":
        required = headers
        numeric = ["YEAR", "CODE_REGION", "CODE_AREA", "MONTHLY_INCOME", "CURRENT_INCOME",
                   "MONEY_INCOME", "FROM_WORK", "CURRENT_TRANSFER", "PROPERTY_INCOME",
                   "NONMONEY_INCOME", "NONCUR_M_INCOME"]
        for row in rows:
            d = row["data"]
            for col in required:
                if not clean(d.get(col)):
                    row["reasons"].append("missing required field: " + col)
            for col in numeric:
                value = parse_number(d.get(col))
                if value is None or value < 0 or (col in ("YEAR", "CODE_REGION", "CODE_AREA") and not value.is_integer()):
                    row["reasons"].append(col + " must be a valid non-negative number")

    elif file_name == "dpm-gd015__1.csv" or file_name == "STATISTIC_FLD.xlsx":
        required = ["PROVINCE_CODE", "PROVINCE_NAME", "AMPHUR_CODE", "AMPHUR_NAME",
                    "MOO_ID", "DIS_TYPE_NAME"]
        year_cols = [h for h in headers if re.fullmatch(r"Y\d{4}", h)]
        for row in rows:
            d = row["data"]
            for col in required:
                if not clean(d.get(col)):
                    row["reasons"].append("missing key field: " + col.strip())
            for col in ("PROVINCE_CODE", "AMPHUR_CODE", "MOO_ID"):
                value = clean(d.get(col))
                if value and not value.isdigit():
                    row["reasons"].append(col + " must contain digits only")
            for col in year_cols:
                value = clean(d.get(col))
                if value and (not value.isdigit() or int(value) < 0):
                    row["reasons"].append(col + " must be a non-negative integer or blank")
        notes.append("ช่องปี Y2562–Y2567 ว่างได้ตามรูปแบบต้นทาง; เก็บเป็น missing/ไม่มีรายการ ไม่แปลงเป็นศูนย์")
        notes.append("ชื่อคอลัมน์บางตัวมีช่องว่างท้ายชื่อ; ควร normalize header ในขั้น clean โดยเก็บ mapping ไว้")

    elif file_name == "2564_by_disaster_type1.csv":
        # Source export has a continuation header and summary blocks mixed into the table.
        amount_cols = headers[2:]
        for row in rows:
            d = row["data"]
            first = clean(d.get("ที่"))
            province = clean(d.get("จังหวัด"))
            if not first and not province:
                row["reasons"].append("header continuation row; not a province record")
                continue
            if "วงเงิน" in first or first.startswith("รวม "):
                row["reasons"].append("summary row; keep outside province-level detail table")
                continue
            if province in ("กรุงเทพฯ", "หน่วยงานในสังกัด"):
                row["reasons"].append("non-province summary row; keep outside province-level detail table")
                continue
            if not first.isdigit() or not province:
                row["reasons"].append("province detail row has invalid sequence or missing province")
            for col in amount_cols:
                value = clean(d.get(col))
                if value in ("", "-", "—"):
                    continue
                if parse_number(value) is None or parse_number(value) < 0:
                    row["reasons"].append("invalid non-negative amount in " + col)
        notes.append("แถวหัวตารางต่อและแถวสรุปถูก quarantine จากตารางระดับจังหวัด ไม่ได้ถือว่าเป็นข้อมูลต้นทางเสีย")

    elif file_name == "Number_of_Affected_Households.xlsx":
        required = headers
        for row in rows:
            d = row["data"]
            for col in required:
                if not clean(d.get(col)):
                    row["reasons"].append("missing required field: " + col)
            count = parse_number(d.get("จำนวน"))
            if count is None or count < 0 or not count.is_integer():
                row["reasons"].append("จำนวน must be a non-negative integer")
        notes.append("ข้อมูลเป็นรายการสรุปหลายประเภท (ตำบล/หมู่บ้าน/ครัวเรือน); อย่ารวมจำนวนต่างหน่วยเข้าด้วยกัน")

    duplicate_indices = exact_duplicate_rows(headers, [row["data"] for row in rows])
    for i in duplicate_indices:
        if not any("exact duplicate" in reason for reason in rows[i]["reasons"]):
            rows[i]["reasons"].append("exact duplicate record; first occurrence retained")

    # Quarantine only rows with explicit errors; preserve source row numbers and raw values.
    for row in rows:
        if row["reasons"]:
            quarantine.append({"source_row": row["row_number"], "reasons": row["reasons"], "data": row["data"]})

    column_stats = []
    for header in headers:
        values = [clean(row["data"].get(header)) for row in rows]
        column_stats.append({
            "column": header,
            "missing_count": sum(v == "" for v in values),
            "unique_nonempty": len({v for v in values if v}),
        })
    return {
        "data_row_count": len(rows),
        "accepted_count": len(rows) - len(quarantine),
        "quarantined_count": len(quarantine),
        "duplicate_rows_quarantined": sum(any("duplicate" in reason for reason in item["reasons"]) for item in quarantine),
        "column_stats": column_stats,
        "notes": notes,
        "quarantine": quarantine,
        "issues": issues,
    }


def run_csv(path):
    raw, encoding = read_csv(path)
    if not raw:
        raise ValueError("empty file")
    # CSV headers are physical row 1; preserve source line numbers.
    rows = [{"row_number": i + 2, "values": row} for i, row in enumerate(raw[1:])]
    result = validate_table(path.name, raw[0], rows)
    report = {"file": path.name, "format": "csv", "encoding": encoding, **result}
    if path.name == "Geographic_Data.csv":
        duplicates = exact_duplicate_rows(
            [clean(header) for header in raw[0]],
            [{clean(header): value for header, value in zip(raw[0], row)} for row in raw[1:]],
        )
        CLEANED_DIR.mkdir(parents=True, exist_ok=True)
        clean_path = CLEANED_DIR / "Geographic_Data_deduplicated.csv"
        with clean_path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(raw[0])
            writer.writerows(row for i, row in enumerate(raw[1:]) if i not in duplicates)
        report["deduplicated_file"] = str(clean_path.relative_to(VALIDATION_DIR)).replace("\\", "/")
        report["deduplicated_row_count"] = len(raw) - 1 - len(duplicates)
    return report


def run_xlsx(path):
    sheets = read_xlsx(path)
    result_sheets = {}
    for name, raw_rows in sheets.items():
        if not raw_rows:
            result_sheets[name] = {"data_row_count": 0, "accepted_count": 0,
                                   "quarantined_count": 0, "column_stats": [], "notes": [],
                                   "quarantine": [], "issues": ["empty worksheet"]}
            continue
        headers = raw_rows[0]["values"]
        rows = raw_rows[1:]
        result_sheets[name] = validate_table(path.name, headers, rows)
    return {"file": path.name, "format": "xlsx", "sheets": result_sheets}


def main():
    if not DATA_DIR.exists():
        raise SystemExit(f"Data directory not found: {DATA_DIR}")
    files = sorted(p for p in DATA_DIR.iterdir() if p.suffix.lower() in (".csv", ".xlsx"))
    if not files:
        raise SystemExit(f"No CSV/XLSX files found in {DATA_DIR}")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    reports = []
    for path in files:
        try:
            report = run_csv(path) if path.suffix.lower() == ".csv" else run_xlsx(path)
            reports.append(report)
            tables = report.get("sheets", {"csv": report})
            for table_name, table in tables.items():
                target = QUARANTINE_DIR / (path.stem + "__" + re.sub(r"[^A-Za-z0-9_-]", "_", table_name) + ".jsonl")
                if not table.get("quarantine"):
                    target.unlink(missing_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("w", encoding="utf-8", newline="\n") as stream:
                    for item in table["quarantine"]:
                        stream.write(json.dumps(item, ensure_ascii=False) + "\n")
                table["quarantine_file"] = str(target.relative_to(VALIDATION_DIR)).replace("\\", "/")
                table.pop("quarantine", None)
        except Exception as exc:
            reports.append({"file": path.name, "status": "failed", "error": str(exc)})

    report_path = REPORT_DIR / "validation_report.json"
    report_path.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"Report: {report_path}")
    for report in reports:
        if report.get("status") == "failed":
            print(f"FAILED {report['file']}: {report['error']}")
            continue
        tables = report.get("sheets", {"csv": report})
        for name, table in tables.items():
            print(f"{report['file']} [{name}]: accepted={table['accepted_count']}, quarantined={table['quarantined_count']}")
    if any(report.get("status") == "failed" for report in reports):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
