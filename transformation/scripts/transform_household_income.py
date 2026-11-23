"""Transform Chiang Mai household income data."""

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "validation"
    / "cleaned"
    / "household_income_cleaned.csv"
)

OUTPUT_DIR = ROOT / "transformation" / "output"
REPORT_DIR = ROOT / "transformation" / "reports"

OUTPUT_FILE = OUTPUT_DIR / "household_income_transformed.csv"
REPORT_FILE = REPORT_DIR / "household_income_transformation_report.json"


COLUMN_MAPPING = {
    "รายการสถิติ": "statistic",
    "อำเภอ": "district",
    "ตำบล": "subdistrict",
    "พื้นที่": "area",
    "ครัวเรือน": "households",
    "รายได้": "income",
    "หน่วย": "unit",
}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(
        INPUT_FILE,
        dtype={
            "อำเภอ": "string",
            "ตำบล": "string",
            "พื้นที่": "string",
            "หน่วย": "string",
        },
    )

    input_rows = len(df)

    missing_columns = [
        column for column in COLUMN_MAPPING
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Keep only the expected source columns and standardize names.
    transformed = df[list(COLUMN_MAPPING)].copy()
    transformed = transformed.rename(columns=COLUMN_MAPPING)

    # Preserve area names and source spelling.
    # In particular, do not modify the source spelling "ทุ่งปี๊".
    text_columns = [
        "statistic",
        "district",
        "subdistrict",
        "area",
        "unit",
    ]

    for column in text_columns:
        transformed[column] = (
            transformed[column]
            .astype("string")
            .str.strip()
        )

    # Convert numeric fields without replacing missing values with zero.
    numeric_errors = {}

    for column in ["households", "income"]:
        original = transformed[column].copy()
        converted = pd.to_numeric(original, errors="coerce")

        invalid_mask = original.notna() & converted.isna()
        numeric_errors[column] = int(invalid_mask.sum())

        transformed[column] = converted

    # Save transformed dataset.
    transformed.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    # Create transformation report.
    report = {
        "dataset": "Chiang Mai Household Income",
        "input_file": str(INPUT_FILE.relative_to(ROOT)),
        "output_file": str(OUTPUT_FILE.relative_to(ROOT)),
        "input_rows": int(input_rows),
        "output_rows": int(len(transformed)),
        "input_columns": int(len(df.columns)),
        "output_columns": int(len(transformed.columns)),
        "columns": list(transformed.columns),
        "missing_values": {
            column: int(transformed[column].isna().sum())
            for column in transformed.columns
        },
        "numeric_conversion_errors": numeric_errors,
        "district_count": int(
            transformed["district"].nunique(dropna=True)
        ),
        "subdistrict_count": int(
            transformed["subdistrict"].nunique(dropna=True)
        ),
        "area_count": int(
            transformed["area"].nunique(dropna=True)
        ),
        "units": sorted(
            transformed["unit"].dropna().unique().tolist()
        ),
        "source_spelling_preserved": {
            "ทุ่งปี๊": bool(
                transformed["subdistrict"]
                .eq("ทุ่งปี๊")
                .any()
            )
        },
        "notes": [
            "All source rows are retained.",
            "Missing numeric values are preserved and not replaced with zero.",
            "Area names and source spelling are preserved.",
            "No join with village mapping is performed in this script.",
            "Income values retain the source unit and definition.",
        ],
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=4,
        )

    print("Household income transformation completed.")
    print(f"Input rows: {input_rows}")
    print(f"Output rows: {len(transformed)}")
    print(f"Output columns: {len(transformed.columns)}")
    print(f"Numeric conversion errors: {numeric_errors}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
