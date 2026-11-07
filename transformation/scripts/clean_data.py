from pathlib import Path
import json
import pandas as pd


# Locate project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]


# Input and output paths
INPUT_FILE = (
    PROJECT_ROOT
    / "validation"
    / "cleaned"
    / "Geographic_Data_deduplicated.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "transformation" / "output"
REPORT_DIR = PROJECT_ROOT / "transformation" / "reports"

OUTPUT_FILE = OUTPUT_DIR / "geographic_data_cleaned.csv"
REPORT_FILE = REPORT_DIR / "geographic_data_cleaning_report.json"


def clean_geographic_data():
    # Create output directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Read validated dataset
    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    original_rows = len(df)
    original_columns = df.columns.tolist()
    missing_before = df.isna().sum().to_dict()

    # Check required columns
    required_columns = [
        "ปี",
        "รายการ",
        "อำเภอ",
        "ตำบล",
        "หมู่ที่",
        "ความเสี่ยง",
        "เหล่งที่มา",
    ]

    missing_columns = [
        col for col in required_columns if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Standardize text values by removing surrounding whitespace
    text_columns = df.select_dtypes(include=["object", "str"]).columns

    for col in text_columns:
        df[col] = df[col].str.strip()

    # Convert year to nullable integer
    year_numeric = pd.to_numeric(df["ปี"], errors="raise")

    if year_numeric.dropna().mod(1).ne(0).any():
        raise ValueError("Year column contains non-integer values")

    df["ปี"] = year_numeric.astype("Int64")

    # Convert village number to nullable integer
    moo_numeric = pd.to_numeric(df["หมู่ที่"], errors="raise")

    if moo_numeric.dropna().mod(1).ne(0).any():
        raise ValueError("หมู่ที่ contains non-integer values")

    df["หมู่ที่"] = moo_numeric.astype("Int64")

    # Check duplicate rows without silently deleting data
    duplicate_count = int(df.duplicated().sum())

    # Save cleaned dataset
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    # Create cleaning report
    report = {
        "dataset": "Geographic_Data",
        "input_file": str(INPUT_FILE.relative_to(PROJECT_ROOT)),
        "output_file": str(OUTPUT_FILE.relative_to(PROJECT_ROOT)),
        "original_rows": original_rows,
        "output_rows": len(df),
        "rows_removed": original_rows - len(df),
        "columns": original_columns,
        "missing_values_before": {
            key: int(value)
            for key, value in missing_before.items()
        },
        "missing_values_after": {
            key: int(value)
            for key, value in df.isna().sum().to_dict().items()
        },
        "duplicate_rows_found": duplicate_count,
        "transformations": [
            "Removed leading and trailing whitespace from text values",
            "Converted year to nullable integer",
            "Converted หมู่ที่ to nullable integer",
            "Preserved missing values",
            "Preserved original column names",
            "Did not remove rows"
        ]
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=4)

    print("===== TRANSFORMATION COMPLETED =====")
    print("Input rows:", original_rows)
    print("Output rows:", len(df))
    print("Rows removed:", original_rows - len(df))
    print("Duplicate rows found:", duplicate_count)
    print("\nOutput file:", OUTPUT_FILE)
    print("Report file:", REPORT_FILE)


if __name__ == "__main__":
    clean_geographic_data()
