"""Data validation & data quality for the CS341 flood project.

Checks per file:
  1. Schema        - required / unexpected columns, header problems, row width
  2. Data types    - int / number / date / code / text per column
  3. Missing       - blank (incl. whitespace-only) values, required vs optional
  4. Duplicates    - exact duplicate rows and duplicate business keys
  5. Invalid values- range, code format, cross-field rules, coordinates
  6. Quarantine    - rows with any ERROR go to validation/quarantine/,
                     WARNINGs stay in the data but are counted in the report.
  7. Cleaned copy  - accepted rows (no ERROR) are written to validation/cleaned/
                     as <name>_cleaned.csv. Only lossless normalisation is applied:
                     whitespace trimmed (blank cells become empty) and numbers stored
                     as text (e.g. "5,294") written as plain numbers. Nothing is
                     corrected, imputed or de-duplicated. Raw files are never modified.
  8. Cross-file    - share of flood Village Codes that exist in village_mapping.json.

Report format (validation/reports/validation_report.json) keeps the keys that
orchestration/lambda_handlers.py reads (results / quarantined_count / status).
"""
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

import openpyxl

DATA_DIR = Path(__file__).parent / "data"
VALIDATION_DIR = Path(__file__).parent.parent / "validation"
REPORT_DIR = VALIDATION_DIR / "reports"
QUARANTINE_DIR = VALIDATION_DIR / "quarantine"
CLEANED_DIR = VALIDATION_DIR / "cleaned"

MAX_EXAMPLES = 5
ERROR, WARNING = "ERROR", "WARNING"

# --------------------------------------------------------------------------
# Schemas  (column -> spec).  type: int | number | date | text
#   required : blank value -> ERROR (row quarantined); otherwise only counted
#   min/max  : numeric range (violation -> ERROR)
#   warn_max : implausibly large value (violation -> WARNING only)
#   digits   : exact digit count, int or tuple of allowed counts (code columns)
# --------------------------------------------------------------------------
COUNT = {"type": "int", "min": 0}
NUM = {"type": "number", "min": 0}
DATE = {"type": "date"}


def code(n, required=True):
    return {"type": "int", "digits": n, "required": required}


# Village codes are 8 digits (province+district+subdistrict+moo) or 9 digits for
# communities inside municipalities (district code + 5 digits, no Moo/Subdistrict).
VILLAGE_CODE = code((8, 9))


FLOOD_2566 = {
    "Incident Name": {"type": "text", "required": True},
    "Disaster Date": {**DATE, "required": True},
    "Province Code": code(2),
    "Province": {"type": "text", "required": True},
    "District Code": code(4),
    "District": {"type": "text", "required": True},
    "Subdistrict Code": code(6, False),
    "Subdistrict": {"type": "text"},
    "Moo": COUNT,
    "Village Code": VILLAGE_CODE,
    "Relief Declared Date": DATE,
    "Disaster Area Date": DATE,
    "Other Announce Date": DATE,
    "End Disaster Date": DATE,
    "Affected People": {**COUNT, "warn_max": 15000},
    "Affected Households": COUNT,
    "Evacuated People": COUNT,
    "Evacuated Households": COUNT,
    "Deaths": COUNT, "Missing": COUNT, "Injured": COUNT,
    "Housing Damage": NUM, "Business Damage": NUM, "Agriculture Damage": NUM,
    "Livestock Damage": NUM, "Fishing Damage": NUM, "Transport Damage": NUM,
    "Health Damage": NUM, "Culture Damage": NUM, "Education/Sports": NUM,
    "Utilities Damage": NUM, "Govt. Locations Damage": NUM,
    "Other Public Benefits": NUM, "Govt Property Damage": NUM,
}

FLOOD_2567 = {
    "_id": {"type": "int", "required": True},
    "Situation name": {"type": "text", "required": True},
    "Disaster Date": {**DATE, "required": True},
    "Province Code": code(2),
    "Province": {"type": "text", "required": True},
    "District Code": code(4),
    "District": {"type": "text", "required": True},
    "Sub-district Code": code(6, False),
    "Moo": COUNT,
    "Village Code": VILLAGE_CODE,
    "Aid Zone Declaration": DATE,
    "Disaster Declaration": DATE,
    "Situation Ended": DATE,
    "Affected People": {**COUNT, "warn_max": 15000},
    "Affected Households": COUNT,
    "Evacuees": COUNT,
    "Evacuees (Households)": COUNT,
    "fatalities_count": COUNT, "Missing Persons": COUNT, "injuries_count": COUNT,
    "Housing (Units)": NUM, "Business (Sites)": NUM, "Agriculture (Acres)": NUM,
    "Livestock (Head)": NUM, "Fisheries (Ponds)": NUM,
    "Transportation (Sites)": NUM, "Health (Sites)": NUM,
    "Religion/Culture (Sites)": NUM, "Education/Sports (Sites)": NUM,
    "Utilities (Sites)": NUM, "Government Sites": NUM,
    "Other Public Benefit (Sites)": NUM, "Gov./Private Property (Units)": NUM,
}

CHIANGMAI = {
    "ปี": {"type": "int", "required": True, "min": 2550, "max": 2580},
    "อำเภอ": {"type": "text", "required": True},
    "ตำบล": COUNT,
    "หมู่บ้าน": COUNT,
    "วันที่เกิดภัย": {**DATE, "required": True},
    "ราษฎร(คน)": COUNT, "ราษฎร(ครัวเรือน)": COUNT,
    "อพยพ(ครัวเรือน)": COUNT, "อพยพ(คน)": COUNT,
    "เสียชีวิต(คน)": COUNT, "สูญหาย(คน)": COUNT, "บาดเจ็บ(คน)": COUNT,
    "บ้านพักอาศัย(หลัง)": COUNT, "บ้านเรือนบางส่วน(หลัง)": COUNT,
}

INCOME = {
    "รายการสถิติ": {"type": "text", "required": True},
    "อำเภอ": {"type": "text", "required": True},
    "ตำบล": {"type": "text"},
    "พื้นที่": {"type": "text", "required": True},
    "ครัวเรือน": {"type": "int", "min": 1, "required": True},
    # average annual household income; values < 1,000 baht are implausible
    # (seen as e.g. 372.827 - probably thousands of baht) and are quarantined
    "รายได้": {"type": "number", "min": 1000, "required": True},
    "หน่วย": {"type": "text", "required": True},
}

VILLAGE = {
    "pcode": {"type": "int", "required": True},
    "pname": {"type": "text", "required": True},
    "acode": {"type": "int", "required": True},
    "aname": {"type": "text", "required": True},
    "tcode": {"type": "int", "required": True},
    "tname": {"type": "text", "required": True},
    "mcode": {"type": "int", "required": True},
    # this file covers Chiang Mai only (pcode 50): use a Chiang Mai bounding box so
    # placeholder coordinates elsewhere in Thailand (e.g. Bangkok 13.7, 100.5) fail
    "oct_side15_lat": {"type": "number", "required": True, "min": 16.5, "max": 20.5},
    "oct_side15_lon": {"type": "number", "required": True, "min": 97.5, "max": 99.8},
    "oct_side15_men": COUNT, "oct_side15_wmen": COUNT,
    "oct_side15_total": COUNT, "oct_side15_house": COUNT,
}

# date_pairs: (earlier, later) must not be reversed
# key: business key; same key with different content -> WARNING
# sums: (total, [parts]) total must be >= sum(parts)  (or == when exact=True)
# le:   (small, big) small must be <= big
FILE_RULES = {
    "flood_2566.csv": {
        "schema": FLOOD_2566,
        "key": ["Village Code", "Disaster Date", "Incident Name"],
        "date_pairs": [("Disaster Date", "End Disaster Date")],
        "le": [("Affected Households", "Affected People"),
               ("Evacuated People", "Affected People")],
        "prefix": [("District Code", "Province Code"),
                   ("Subdistrict Code", "District Code"),
                   ("Village Code", "Subdistrict Code")],
    },
    "flood_2567.csv": {
        "schema": FLOOD_2567,
        "key": ["_id"],
        "date_pairs": [("Disaster Date", "Situation Ended")],
        "le": [("Affected Households", "Affected People"),
               ("Evacuees", "Affected People")],
        "prefix": [("District Code", "Province Code"),
                   ("Sub-district Code", "District Code"),
                   ("Village Code", "Sub-district Code")],
    },
    "chiangmai_damage.xlsx": {
        "schema": CHIANGMAI,
        "key": ["ปี", "อำเภอ", "หมู่บ้าน", "วันที่เกิดภัย"],
        "le": [("ราษฎร(ครัวเรือน)", "ราษฎร(คน)"), ("อพยพ(คน)", "ราษฎร(คน)")],
        "year_match": ("ปี", "วันที่เกิดภัย"),
    },
    "household_income.xlsx": {
        "schema": INCOME,
        "key": ["อำเภอ", "ตำบล", "พื้นที่"],
        "le": [],
    },
    "village_mapping.json": {
        "schema": VILLAGE,
        "key": ["mcode"],
        "sums": [("oct_side15_total", ["oct_side15_men", "oct_side15_wmen"])],
    },
}

# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
DATE_FORMATS = ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d",
                "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S")


def clean(value):
    return str(value if value is not None else "").strip()


def json_default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def parse_number(text):
    """Return float or None. Accepts thousands separators and '.00'."""
    text = clean(text).replace(",", "")
    if not re.fullmatch(r"[+-]?(\d+(\.\d*)?|\.\d+)", text):
        return None
    return float(text)


def parse_date(value):
    """Return datetime or None. Buddhist-Era years (> 2400) are converted."""
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, date):
        dt = datetime(value.year, value.month, value.day)
    else:
        text = clean(value)
        dt = None
        for fmt in DATE_FORMATS:
            try:
                dt = datetime.strptime(text, fmt)
                break
            except ValueError:
                continue
        if dt is None:
            return None
    if dt.year > 2400:
        try:
            dt = dt.replace(year=dt.year - 543)
        except ValueError:
            return None
    return dt if 1990 <= dt.year <= 2100 else None


def check_cell(value, spec):
    """Return (parsed_value, problem_or_None). Blank is handled by caller."""
    kind = spec["type"]
    text = clean(value)
    if kind == "text":
        return text, None
    if kind == "date":
        dt = parse_date(value)
        return dt, None if dt else "invalid date"
    number = parse_number(value) if not isinstance(value, (int, float)) \
        or isinstance(value, bool) else float(value)
    if number is None:
        return None, f"not a number ({text[:30]!r})"
    if kind == "int":
        if number != int(number):
            return None, f"not an integer ({text[:30]!r})"
        if "digits" in spec:
            allowed = spec["digits"] if isinstance(spec["digits"], tuple) else (spec["digits"],)
            if len(str(int(number))) not in allowed:
                return None, (f"code must have {' or '.join(map(str, allowed))} digits "
                              f"(got {text[:30]!r})")
    if "min" in spec and number < spec["min"]:
        return None, f"below minimum {spec['min']} ({text[:30]!r})"
    if "max" in spec and number > spec["max"]:
        return None, f"above maximum {spec['max']} ({text[:30]!r})"
    return (int(number) if kind == "int" else number), None


class Findings:
    """Collects rule hits with counts and a few examples for the report."""

    def __init__(self):
        self.counts = Counter()
        self.examples = defaultdict(list)
        self.severity = {}

    def add(self, rule, severity, row_no, detail):
        self.counts[rule] += 1
        self.severity[rule] = severity
        if len(self.examples[rule]) < MAX_EXAMPLES:
            self.examples[rule].append({"source_row": row_no, "detail": detail})

    def summary(self):
        return {
            rule: {"severity": self.severity[rule], "count": n,
                   "examples": self.examples[rule]}
            for rule, n in sorted(self.counts.items())
        }


# --------------------------------------------------------------------------
# core validation
# --------------------------------------------------------------------------
def validate_table(headers, data_rows, rules=None, sink=None):
    headers = [clean(h) for h in headers]
    schema = (rules or {}).get("schema")
    findings = Findings()
    issues = []
    notes = []

    # ---- 1. schema -------------------------------------------------------
    if not headers:
        issues.append("missing header row")
    if any(not h for h in headers):
        issues.append("blank column name")
    dup_cols = [h for h, n in Counter(headers).items() if h and n > 1]
    if dup_cols:
        issues.append("duplicate column names: " + ", ".join(dup_cols))

    schema_result = None
    if schema:
        required_cols = [c for c, s in schema.items() if s.get("required")]
        missing_required = [c for c in required_cols if c not in headers]
        missing_optional = [c for c in schema
                            if c not in headers and c not in missing_required]
        unexpected = [h for h in headers if h and h not in schema]
        if missing_required:
            issues.append("missing required columns: " + ", ".join(missing_required))
        schema_result = {
            "expected_columns": len(schema),
            "missing_required_columns": missing_required,
            "missing_optional_columns": missing_optional,
            "unexpected_columns": unexpected,
        }
        notes.append("Schema, type, range and cross-field rules applied.")
    else:
        notes.append("No schema registered for this file; structural checks only.")

    width = len(headers)
    index = {h: i for i, h in enumerate(headers) if h}
    key_cols = [c for c in (rules or {}).get("key", []) if c in index]

    quarantine = []
    seen_rows = {}
    seen_keys = {}
    missing_by_col = [0] * width
    unique_by_col = [set() for _ in headers]
    type_failures = Counter()
    total = accepted = exact_dups = key_dups = 0

    for source_row, values in data_rows:
        total += 1
        values = list(values)
        reasons = []          # ERRORs  -> quarantine
        warns = []            # WARNINGs -> reported only

        def err(rule, detail, column=None):
            reasons.append(f"{rule}: {detail}")
            findings.add(rule, ERROR, source_row, detail)
            if column:
                type_failures[column] += 1

        def warn(rule, detail):
            warns.append(f"{rule}: {detail}")
            findings.add(rule, WARNING, source_row, detail)

        if len(values) != width:
            err("row_width", f"{len(values)} values; expected {width}")
        padded = (values + [None] * width)[:width]
        raw = [clean(v) for v in padded]

        for i, text in enumerate(raw):
            if text:
                unique_by_col[i].add(text)
            else:
                missing_by_col[i] += 1

        # ---- 4a. exact duplicates -----------------------------------------
        signature = tuple(raw)
        if signature in seen_rows:
            exact_dups += 1
            err("exact_duplicate",
                f"identical to row {seen_rows[signature]}")
        else:
            seen_rows[signature] = source_row

        # ---- 2/3/5. per-column type, missing, range -----------------------
        parsed = {}
        if schema:
            for col, spec in schema.items():
                if col not in index:
                    continue
                value = padded[index[col]]
                if not clean(value):
                    if spec.get("required"):
                        err("missing_required", f"{col} is blank", col)
                    continue
                result, problem = check_cell(value, spec)
                if not problem and spec["type"] in ("int", "number"):
                    if isinstance(value, str) and "," in value:
                        warn("number_stored_as_text",
                             f"{col}: {value.strip()!r} has a thousands separator")
                    if "warn_max" in spec and result > spec["warn_max"]:
                        warn("suspiciously_large_value",
                             f"{col}={result} exceeds {spec['warn_max']} for one village")
                if problem:
                    kind = {"date": "invalid_date", "text": "invalid_text"}.get(
                        spec["type"], "invalid_number")
                    err(kind, f"{col}: {problem}", col)
                else:
                    parsed[col] = result
                    if spec["type"] in ("int", "number"):
                        raw[index[col]] = (str(int(result)) if float(result).is_integer()
                                           else repr(float(result)))

            # ---- 5. cross-field rules --------------------------------------
            for earlier, later in rules.get("date_pairs", []):
                if earlier in parsed and later in parsed and parsed[later] < parsed[earlier]:
                    warn("date_order", f"{later} is before {earlier}")
            for small, big in rules.get("le", []):
                if small in parsed and big in parsed and parsed[small] > parsed[big]:
                    warn("subset_exceeds_total", f"{small} ({parsed[small]}) > {big} ({parsed[big]})")
            for total_col, parts in rules.get("sums", []):
                if total_col in parsed and all(p in parsed for p in parts):
                    if parsed[total_col] != sum(parsed[p] for p in parts):
                        warn("total_mismatch", f"{total_col} != sum({', '.join(parts)})")
            for child, parent in rules.get("prefix", []):
                if child in parsed and parent in parsed and \
                        not str(parsed[child]).startswith(str(parsed[parent])):
                    err("code_hierarchy", f"{child}={parsed[child]} does not start with {parent}={parsed[parent]}")
            if "year_match" in rules:
                ycol, dcol = rules["year_match"]
                if ycol in parsed and dcol in parsed and parsed[ycol] - 543 != parsed[dcol].year:
                    warn("year_vs_date", f"{ycol}={parsed[ycol]} but {dcol} year is {parsed[dcol].year}")

        # ---- 4b. duplicate business key with different content -----------
        if key_cols and not any(not raw[index[c]] for c in key_cols):
            key = tuple(raw[index[c]] for c in key_cols)
            if key in seen_keys and signature != seen_keys[key][1]:
                key_dups += 1
                warn("duplicate_key", f"key {dict(zip(key_cols, key))} first seen at row {seen_keys[key][0]}")
            seen_keys.setdefault(key, (source_row, signature))

        if reasons:
            quarantine.append({
                "source_row": source_row,
                "reasons": reasons,
                "warnings": warns,
                "data": {h or f"unnamed_column_{i + 1}": raw[i]
                         for i, h in enumerate(headers)},
            })
        else:
            accepted += 1
            if sink is not None:
                sink.append(raw)

    warning_count = sum(n for r, n in findings.counts.items()
                        if findings.severity[r] == WARNING)
    if issues and schema_result and schema_result["missing_required_columns"]:
        status = "FAIL"
    elif issues or quarantine or warning_count:
        status = "WARNING"
    else:
        status = "PASS"

    def col_name(i, h):
        return h or f"unnamed_column_{i + 1}"

    result = {
        "status": status,
        "issues": issues,
        "notes": notes,
        "row_count": total,
        "accepted_count": accepted,
        "quarantined_count": len(quarantine),
        "duplicate_count": exact_dups,
        "duplicate_key_count": key_dups,
        "warning_count": warning_count,
        "columns": headers,
        "schema": schema_result,
        "rule_violations": findings.summary(),
        "type_failures_by_column": dict(type_failures),
        "missing_values_by_column": {col_name(i, h): missing_by_col[i]
                                     for i, h in enumerate(headers)},
        "missing_pct_by_column": {col_name(i, h): round(100 * missing_by_col[i] / total, 2) if total else 0
                                  for i, h in enumerate(headers)},
        "unique_values_by_column": {col_name(i, h): len(unique_by_col[i])
                                    for i, h in enumerate(headers)},
    }
    return result, quarantine


# --------------------------------------------------------------------------
# file readers
# --------------------------------------------------------------------------
def write_cleaned(name, headers, rows):
    """Write accepted rows to validation/cleaned/<name>_cleaned.csv."""
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    out = CLEANED_DIR / f"{name}_cleaned.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)
    return str(out)


def validate_csv(path, rules=None):
    last_error = None
    for encoding in ("utf-8-sig", "cp874"):
        try:
            with path.open(encoding=encoding, newline="") as stream:
                reader = csv.reader(stream)
                headers = next(reader, [])
                sink = []
                result, quarantine = validate_table(
                    headers, enumerate(reader, start=2), rules, sink)
                result["cleaned_file"] = write_cleaned(path.stem, result["columns"], sink)
                result["encoding"] = encoding
                result["file_type"] = "CSV"
                return result, quarantine
        except UnicodeDecodeError as error:
            last_error = error
    raise ValueError(f"Unsupported CSV encoding: {last_error}")


def validate_xlsx(path, rules=None):
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    results, all_quarantine = {}, []
    try:
        for sheet in workbook.worksheets:
            iterator = sheet.iter_rows(values_only=True)
            headers = next(iterator, [])
            rows = ((n, v) for n, v in enumerate(iterator, start=2)
                    if any(x is not None and clean(x) for x in v))
            sink = []
            result, quarantine = validate_table(headers, rows, rules, sink)
            name = path.stem if len(workbook.worksheets) == 1 else f"{path.stem}_{sheet.title}"
            result["cleaned_file"] = write_cleaned(name, result["columns"], sink)
            result["file_type"] = "XLSX"
            result["sheet_name"] = sheet.title
            results[sheet.title] = result
            for item in quarantine:
                item["sheet_name"] = sheet.title
                all_quarantine.append(item)
    finally:
        workbook.close()

    statuses = [x["status"] for x in results.values()]
    return {
        "file_type": "XLSX",
        "status": ("FAIL" if "FAIL" in statuses else
                   "WARNING" if any(s != "PASS" for s in statuses) else "PASS"),
        "sheets": results,
        "row_count": sum(x["row_count"] for x in results.values()),
        "accepted_count": sum(x["accepted_count"] for x in results.values()),
        "quarantined_count": len(all_quarantine),
    }, all_quarantine


def validate_json(path, rules=None):
    with path.open(encoding="utf-8") as stream:
        data = json.load(stream)
    records = data if isinstance(data, list) else [data] if isinstance(data, dict) else None
    if records is None:
        raise ValueError("JSON root must be an object or a list")
    if not records:
        return {"file_type": "JSON", "status": "WARNING", "row_count": 0,
                "accepted_count": 0, "quarantined_count": 0,
                "issues": ["JSON contains no records"]}, []
    bad = [i for i, r in enumerate(records, 1) if not isinstance(r, dict)]
    if bad:
        raise ValueError(f"JSON records must be objects (bad at {bad[:5]})")

    headers = list(dict.fromkeys(k for r in records for k in r))
    rows = ((i, [r.get(h) for h in headers]) for i, r in enumerate(records, 1))
    sink = []
    result, quarantine = validate_table(headers, rows, rules, sink)
    result["cleaned_file"] = write_cleaned(path.stem, result["columns"], sink)
    result["file_type"] = "JSON"
    return result, quarantine


# --------------------------------------------------------------------------
def read_cleaned(name):
    path = CLEANED_DIR / f"{name}_cleaned.csv"
    if not path.exists():
        return None
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def cross_file_checks():
    """Referential check: flood Village Codes that exist in village_mapping."""
    mapping = read_cleaned("village_mapping")
    if not mapping:
        return {}
    known = {row["mcode"] for row in mapping}
    q_path = QUARANTINE_DIR / "village_mapping_quarantine.json"
    if q_path.exists():  # quarantined villages still exist as join keys
        known |= {x["data"].get("mcode") for x in json.loads(q_path.read_text(encoding="utf-8"))}
    provinces = {row["pcode"] for row in mapping}
    out = {}
    for name in ("flood_2566", "flood_2567"):
        rows = read_cleaned(name)
        if not rows:
            continue
        in_scope = [r for r in rows if r.get("Province Code") in provinces]
        matched = sum(1 for r in in_scope if r.get("Village Code") in known)
        out[name] = {
            "mapping_provinces": sorted(provinces),
            "rows_in_mapping_provinces": len(in_scope),
            "rows_with_village_code_in_mapping": matched,
            "match_pct": round(100 * matched / len(in_scope), 2) if in_scope else None,
            "unmatched_examples": [r["Village Code"] for r in in_scope
                                   if r.get("Village Code") not in known][:5],
        }
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args()
    data_dir = args.data_dir

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        return

    files = sorted(p for p in data_dir.iterdir()
                   if p.is_file() and p.suffix.lower() in (".csv", ".xlsx", ".json"))
    if not files:
        print("No supported data files found.")
        return

    overall = {"files_checked": 0, "files_passed": 0, "files_with_warnings": 0,
               "files_failed": 0, "results": {}}

    for path in files:
        print(f"\nValidating: {path.name}")
        rules = FILE_RULES.get(path.name)
        if not rules:
            print("  (no schema registered - structural checks only)")
        try:
            suffix = path.suffix.lower()
            if suffix == ".csv":
                result, quarantine = validate_csv(path, rules)
            elif suffix == ".xlsx":
                result, quarantine = validate_xlsx(path, rules)
            else:
                result, quarantine = validate_json(path, rules)

            result["file_name"] = path.name
            overall["files_checked"] += 1
            status = result.get("status")
            if status == "PASS":
                overall["files_passed"] += 1
            elif status == "FAIL":
                overall["files_failed"] += 1
            else:
                overall["files_with_warnings"] += 1

            q_path = QUARANTINE_DIR / (path.stem + "_quarantine.json")
            if quarantine:
                q_path.write_text(json.dumps(quarantine, ensure_ascii=False,
                                             indent=2, default=json_default),
                                  encoding="utf-8")
                result["quarantine_file"] = str(q_path)
            elif q_path.exists():  # remove stale file from an earlier run
                q_path.unlink()

            overall["results"][path.name] = result

            print(f"  Rows: {result.get('row_count', 0)}  "
                  f"Accepted: {result.get('accepted_count', 0)}  "
                  f"Quarantined: {result.get('quarantined_count', 0)}  "
                  f"Status: {status}")
            tables = result.get("sheets", {"": result}).values()
            for table in tables:
                for rule, info in table.get("rule_violations", {}).items():
                    print(f"    [{info['severity']}] {rule}: {info['count']}")

        except Exception as error:
            overall["files_checked"] += 1
            overall["files_failed"] += 1
            overall["results"][path.name] = {"status": "FAIL", "error": str(error)}
            print(f"  FAILED: {error}")

    overall["cross_file_checks"] = cross_file_checks()
    for name, info in overall["cross_file_checks"].items():
        print(f"Cross-file {name}: {info['rows_with_village_code_in_mapping']}/"
              f"{info['rows_in_mapping_provinces']} Village Codes found in village_mapping "
              f"({info['match_pct']}%)")

    report_path = REPORT_DIR / "validation_report.json"
    report_path.write_text(json.dumps(overall, ensure_ascii=False, indent=2,
                                      default=json_default), encoding="utf-8")

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