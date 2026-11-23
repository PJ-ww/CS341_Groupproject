
"""
Transform Chiang Mai flood damage dataset.

Input:
    validation/cleaned/chiangmai_damage_cleaned.csv

Output:
    transformation/output/chiangmai_damage_transformed.csv
    transformation/reports/damage_transformation_report.json
"""

import json
from pathlib import Path

import pandas as pd


# ==================================================
# 1. PROJECT PATHS
# ==================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "validation"
    / "cleaned"
    / "chiangmai_damage_cleaned.csv"
)

OUTPUT_DIR = ROOT / "transformation" / "output"
REPORT_DIR = ROOT / "transformation" / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# 2. COLUMN MAPPING
# ==================================================

COLUMN_MAPPING = {
    "source_year": "ปี",
    "district": "อำเภอ",
    "subdistrict_id": "ตำบล",
    "village_id": "หมู่บ้าน",
    "disaster_date": "วันที่เกิดภัย",
    "affected_people": "ราษฎร(คน)",
    "affected_households": "ราษฎร(ครัวเรือน)",
    "evacuated_households": "อพยพ(ครัวเรือน)",
    "evacuated_people": "อพยพ(คน)",
    "deaths": "เสียชีวิต(คน)",
    "missing_people": "สูญหาย(คน)",
    "injured_people": "บาดเจ็บ(คน)",
    "houses_damaged": "บ้านพักอาศัย(หลัง)",
    "partially_damaged_houses": "บ้านเรือนบางส่วน(หลัง)",
}


# Numeric fields
NUMERIC_COLUMNS = [
    "source_year",
    "affected_people",
    "affected_households",
    "evacuated_households",
    "evacuated_people",
    "deaths",
    "missing_people",
    "injured_people",
    "houses_damaged",
    "partially_damaged_houses",
]


# Identifier and text fields
TEXT_COLUMNS = [
    "district",
    "subdistrict_id",
    "village_id",
]


# ==================================================
# 3. HELPER FUNCTIONS
# ==================================================

def clean_text(series):
    """Trim whitespace and preserve missing values."""

    result = series.astype("string").str.strip()

    return result.replace("", pd.NA)


def convert_numeric(series):
    """Convert numeric values without replacing missing values with zero."""

    cleaned = clean_text(series)

    numeric = pd.to_numeric(
        cleaned.str.replace(",", "", regex=False),
        errors="coerce",
    )

    errors = int(
        (cleaned.notna() & numeric.isna()).sum()
    )

    return numeric, errors


# ==================================================
# 4. MAIN TRANSFORMATION
# ==================================================

def main():

    print("\n===== START DAMAGE TRANSFORMATION =====")

    # --------------------------------------------------
    # 4.1 Check input file
    # --------------------------------------------------

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    # --------------------------------------------------
    # 4.2 Read source data
    # --------------------------------------------------

    df = pd.read_csv(
        INPUT_FILE,
        dtype=str,
    )

    input_rows = len(df)

    print("Input rows:", input_rows)

    # --------------------------------------------------
    # 4.3 Check required columns
    # --------------------------------------------------

    missing_columns = [
        source_column
        for source_column in COLUMN_MAPPING.values()
        if source_column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # --------------------------------------------------
    # 4.4 Create standardized dataset
    # --------------------------------------------------

    output = pd.DataFrame()

    # Generate a stable identifier based on source row order.
    output["source_record_id"] = [
        f"damage-row-{i:06d}"
        for i in range(1, input_rows + 1)
    ]

    # Rename source columns.
    for target_column, source_column in COLUMN_MAPPING.items():
        output[target_column] = df[source_column]

    # --------------------------------------------------
    # 4.5 Clean text and identifiers
    # --------------------------------------------------

    for column in TEXT_COLUMNS:
        output[column] = clean_text(output[column])

    # --------------------------------------------------
    # 4.6 Convert numeric columns
    # --------------------------------------------------

    numeric_conversion_errors = {}

    for column in NUMERIC_COLUMNS:

        converted, error_count = convert_numeric(
            output[column]
        )

        output[column] = converted

        numeric_conversion_errors[column] = error_count

    # --------------------------------------------------
    # 4.7 Standardize disaster dates
    # --------------------------------------------------

    original_dates = clean_text(
        output["disaster_date"]
    )

    parsed_dates = pd.to_datetime(
    original_dates,
    errors="coerce",
    )

    date_conversion_errors = int(
        (
            original_dates.notna()
            & parsed_dates.isna()
        ).sum()
    )

    output["disaster_date"] = (
        parsed_dates.dt.strftime("%Y-%m-%d")
        .astype("string")
    )

    # --------------------------------------------------
    # 4.8 Preserve all source records
    # --------------------------------------------------

    output = output.reset_index(drop=True)

    # --------------------------------------------------
    # 4.9 Export transformed dataset
    # --------------------------------------------------

    output_file = (
        OUTPUT_DIR
        / "chiangmai_damage_transformed.csv"
    )

    output.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig",
    )

    # --------------------------------------------------
    # 4.10 Count records by year
    # --------------------------------------------------

    rows_by_year = {}

    year_counts = (
        output["source_year"]
        .value_counts(dropna=False)
        .sort_index()
    )

    for year, count in year_counts.items():

        if pd.notna(year):
            rows_by_year[str(int(year))] = int(count)

    # --------------------------------------------------
    # 4.11 Check missing values
    # --------------------------------------------------

    missing_values = {
        column: int(output[column].isna().sum())
        for column in output.columns
    }

    # --------------------------------------------------
    # 4.12 Check duplicate location and date records
    # --------------------------------------------------

    duplicate_subset = [
        "source_year",
        "district",
        "subdistrict_id",
        "village_id",
        "disaster_date",
    ]

    duplicate_location_date_rows = int(
        output.duplicated(
            subset=duplicate_subset,
            keep=False,
        ).sum()
    )

    # --------------------------------------------------
    # 4.13 Build transformation report
    # --------------------------------------------------

    report = {
        "dataset": "Chiang Mai Damage",

        "input_file": str(
            INPUT_FILE.relative_to(ROOT)
        ),

        "output_file": str(
            output_file.relative_to(ROOT)
        ),

        "input_rows": input_rows,
        "output_rows": len(output),

        "input_columns": len(df.columns),
        "output_columns": len(output.columns),

        "rows_by_year": rows_by_year,

        "missing_values": missing_values,

        "numeric_conversion_errors": (
            numeric_conversion_errors
        ),

        "date_conversion_errors": (
            date_conversion_errors
        ),

        "duplicate_location_date_rows": (
            duplicate_location_date_rows
        ),

        "processing_notes": [
            "All source records are retained.",
            "Subdistrict and village identifiers are preserved as strings.",
            "Numeric values are converted without replacing missing values with zero.",
            "Disaster dates are standardized to YYYY-MM-DD.",
            "Records are not aggregated across different disaster dates.",
        ],
    }

    report_file = (
        REPORT_DIR
        / "damage_transformation_report.json"
    )

    with open(
        report_file,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=4,
        )

    # --------------------------------------------------
    # 4.14 Print transformation results
    # --------------------------------------------------

    print("\n===== DAMAGE TRANSFORMATION RESULTS =====")

    print("Input rows:", input_rows)
    print("Output rows:", len(output))
    print("Output columns:", len(output.columns))

    print("\nRows by year:")

    for year, count in rows_by_year.items():
        print(f"{year}: {count}")

    print("\nMissing values:")

    for column, count in missing_values.items():

        if count > 0:
            print(f"{column}: {count}")

    print(
        "\nDate conversion errors:",
        date_conversion_errors,
    )

    print("\nNumeric conversion errors:")

    for column, count in numeric_conversion_errors.items():

        if count > 0:
            print(f"{column}: {count}")

    print(
        "\nDuplicate location/date rows:",
        duplicate_location_date_rows,
    )

    print("\nSaved dataset:", output_file)
    print("Saved report:", report_file)

    # --------------------------------------------------
    # 4.15 Basic validation
    # --------------------------------------------------

    assert len(output) == input_rows, (
        "Row count changed during transformation"
    )

    assert output["source_record_id"].is_unique, (
        "Duplicate source record IDs found"
    )

    assert output["source_year"].notna().all(), (
        "Some records have missing source years"
    )

    print("\nDAMAGE TRANSFORMATION COMPLETED SUCCESSFULLY")


# ==================================================
# 5. RUN SCRIPT
# ==================================================

if __name__ == "__main__":
    main()
