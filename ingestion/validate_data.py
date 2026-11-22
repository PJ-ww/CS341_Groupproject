
import csv
import json
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import openpyxl

DATA_DIR = Path(__file__).parent / "data"
VALIDATION_DIR = Path(__file__).parent.parent / "validation"
REPORT_DIR = VALIDATION_DIR / "reports"
QUARANTINE_DIR = VALIDATION_DIR / "quarantine"


def clean(value):
    return str(value if value is not None else "").strip()


def json_default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def row_signature(row):
    return tuple(clean(value) for value in row)


def validate_table(headers, data_rows):
    normalized_headers = [clean(value) for value in headers]
    issues = []
    notes = [
        "Structural validation only; business rules are not yet defined.",
        "Original column names and values are preserved."
    ]

    if not normalized_headers:
        issues.append("missing header row")

    if any(not name for name in normalized_headers):
        issues.append("blank column name")

    duplicates = [
        name for name, count in Counter(normalized_headers).items()
        if name and count > 1
    ]
    if duplicates:
        issues.append("duplicate column names: " + ", ".join(duplicates))

    accepted = 0
    quarantine = []
    seen = set()
    missing_by_column = [0] * len(normalized_headers)
    unique_by_column = [set() for _ in normalized_headers]
    duplicate_count = 0
    total_rows = 0

    for source_row, values in data_rows:
        total_rows += 1
        reasons = []
        values = list(values)

        if len(values) != len(normalized_headers):
            reasons.append(
                f"row width differs from header "
                f"({len(values)} values; expected {len(normalized_headers)})"
            )

        padded = (values + [""] * len(normalized_headers))[
            :len(normalized_headers)
        ]

        signature = row_signature(padded)

        if signature in seen:
            reasons.append("exact duplicate record")
            duplicate_count += 1
        else:
            seen.add(signature)

        for index, value in enumerate(padded):
            value = clean(value)
            if not value:
                missing_by_column[index] += 1
            else:
                unique_by_column[index].add(value)

        if reasons:
            quarantine.append({
                "source_row": source_row,
                "reasons": reasons,
                "data": {
                    header or f"unnamed_column_{index + 1}": padded[index]
                    for index, header in enumerate(normalized_headers)
                }
            })
        else:
            accepted += 1

    return {
        "status": "PASS" if not issues else "WARNING",
        "issues": issues,
        "notes": notes,
        "row_count": total_rows,
        "accepted_count": accepted,
        "quarantined_count": len(quarantine),
        "duplicate_count": duplicate_count,
        "columns": normalized_headers,
        "missing_values_by_column": {
            header or f"unnamed_column_{index + 1}": missing_by_column[index]
            for index, header in enumerate(normalized_headers)
        },
        "unique_values_by_column": {
            header or f"unnamed_column_{index + 1}": len(unique_by_column[index])
            for index, header in enumerate(normalized_headers)
        }
    }, quarantine


def validate_csv(path):
    last_error = None

    for encoding in ("utf-8-sig", "cp874"):
        try:
            with path.open(encoding=encoding, newline="") as stream:
                reader = csv.reader(stream)
                headers = next(reader, [])
                rows = enumerate(reader, start=2)

                result, quarantine = validate_table(headers, rows)
                result["encoding"] = encoding
                result["file_type"] = "CSV"
                return result, quarantine

        except UnicodeDecodeError as error:
            last_error = error

    raise ValueError(f"Unsupported CSV encoding: {last_error}")


def validate_xlsx(path):
    workbook = openpyxl.load_workbook(
        path, read_only=True, data_only=True
    )

    results = {}
    all_quarantine = []

    try:
        for sheet in workbook.worksheets:
            iterator = sheet.iter_rows(values_only=True)
            headers = next(iterator, [])

            rows = (
                (row_number, values)
                for row_number, values in enumerate(iterator, start=2)
                if any(value is not None and clean(value) for value in values)
            )

            result, quarantine = validate_table(headers, rows)
            result["file_type"] = "XLSX"
            result["sheet_name"] = sheet.title

            results[sheet.title] = result

            for item in quarantine:
                item["sheet_name"] = sheet.title
                all_quarantine.append(item)

    finally:
        workbook.close()

    return {
        "file_type": "XLSX",
        "status": (
            "WARNING"
            if any(x["status"] != "PASS" for x in results.values())
            else "PASS"
        ),
        "sheets": results,
        "row_count": sum(x["row_count"] for x in results.values()),
        "accepted_count": sum(x["accepted_count"] for x in results.values()),
        "quarantined_count": len(all_quarantine)
    }, all_quarantine


def validate_json(path):
    with path.open(encoding="utf-8") as stream:
        data = json.load(stream)

    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        records = [data]
    else:
        raise ValueError("JSON root must be an object or a list")

    if not records:
        return {
            "file_type": "JSON",
            "status": "WARNING",
            "row_count": 0,
            "accepted_count": 0,
            "quarantined_count": 0,
            "issues": ["JSON contains no records"]
        }, []

    if not all(isinstance(record, dict) for record in records):
        raise ValueError("JSON records must be objects")

    headers = list(dict.fromkeys(
        key for record in records for key in record.keys()
    ))

    rows = (
        (index, [record.get(header) for header in headers])
        for index, record in enumerate(records, start=1)
    )

    result, quarantine = validate_table(headers, rows)
    result["file_type"] = "JSON"

    return result, quarantine


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    if not DATA_DIR.exists():
        print(f"Data directory not found: {DATA_DIR}")
        return

    files = sorted(
        path for path in DATA_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in (".csv", ".xlsx", ".json")
    )

    if not files:
        print("No supported data files found.")
        return

    overall = {
        "files_checked": 0,
        "files_passed": 0,
        "files_with_warnings": 0,
        "files_failed": 0,
        "results": {}
    }

    for path in files:
        print(f"\nValidating: {path.name}")

        try:
            suffix = path.suffix.lower()

            if suffix == ".csv":
                result, quarantine = validate_csv(path)
            elif suffix == ".xlsx":
                result, quarantine = validate_xlsx(path)
            else:
                result, quarantine = validate_json(path)

            result["file_name"] = path.name

            overall["files_checked"] += 1

            if result.get("status") == "PASS":
                overall["files_passed"] += 1
            elif result.get("status") == "WARNING":
                overall["files_with_warnings"] += 1

            if quarantine:
                quarantine_path = QUARANTINE_DIR / (
                        path.stem + "_quarantine.json"
                )
                quarantine_path.write_text(
                    json.dumps(
                        quarantine,
                        ensure_ascii=False,
                        indent=2,
                        default=json_default
                    ),
                    encoding="utf-8"
                )
                result["quarantine_file"] = str(quarantine_path)

            overall["results"][path.name] = result

            print(f"Rows: {result.get('row_count', 0)}")
            print(f"Accepted: {result.get('accepted_count', 0)}")
            print(f"Quarantined: {result.get('quarantined_count', 0)}")
            print(f"Status: {result.get('status', 'PASS')}")

        except Exception as error:
            overall["files_checked"] += 1
            overall["files_failed"] += 1
            overall["results"][path.name] = {
                "status": "FAIL",
                "error": str(error)
            }
            print(f"FAILED: {error}")

    report_path = REPORT_DIR / "validation_report.json"
    report_path.write_text(
        json.dumps(
            overall,
            ensure_ascii=False,
            indent=2,
            default=json_default
        ),
        encoding="utf-8"
    )

    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Files checked: {overall['files_checked']}")
    print(f"Passed: {overall['files_passed']}")
    print(f"Warnings: {overall['files_with_warnings']}")
    print(f"Failed: {overall['files_failed']}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
