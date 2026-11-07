
from pathlib import Path
import pandas as pd
import json

# PATH CONFIGURATION

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "transformation"
    / "output"
    / "geographic_data_cleaned.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "transformation" / "output"
REPORT_DIR = PROJECT_ROOT / "transformation" / "reports"

OUTPUT_FILE = OUTPUT_DIR / "geographic_data_standardized.csv"
REPORT_FILE = REPORT_DIR / "geographic_data_standardization_report.json"


# STANDARDIZATION CONFIGURATION

RISK_ORDER = [
    "เสี่ยงต่ำมาก",
    "เสี่ยงต่ำ",
    "เสี่ยงปานกลาง",
    "เสี่ยงสูง",
    "เสี่ยงสูงมาก",
]

REQUIRED_COLUMNS = [
    "ปี",
    "รายการ",
    "อำเภอ",
    "ตำบล",
    "หมู่ที่",
    "ความเสี่ยง",
    "เหล่งที่มา",
]


# MAIN FUNCTION

def main():

    print("===== STANDARDIZATION STARTED =====")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Read cleaned data
    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    original_rows = len(df)

    # Check required columns
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Check risk categories
    unknown_risks = sorted(
        set(df["ความเสี่ยง"].dropna().unique())
        - set(RISK_ORDER)
    )

    if unknown_risks:
        raise ValueError(
            f"Unknown risk categories: {unknown_risks}"
        )

    # Standardize risk category order
    df["ความเสี่ยง"] = pd.Categorical(
        df["ความเสี่ยง"],
        categories=RISK_ORDER,
        ordered=True
    )

    # Standardize numeric columns
    df["ปี"] = pd.to_numeric(df["ปี"], errors="raise").astype("Int64")
    df["หมู่ที่"] = pd.to_numeric(df["หมู่ที่"], errors="raise").astype("Int64")

    # Verify data types
    if not pd.api.types.is_integer_dtype(df["ปี"]):
        raise TypeError("ปี must be an integer column")
    
    if not pd.api.types.is_integer_dtype(df["หมู่ที่"]):
        raise TypeError("หมู่ที่ must be an integer column")

    # Export standardized data
    # Convert categorical values to strings for CSV compatibility
    export_df = df.copy()
    export_df["ความเสี่ยง"] = (
        export_df["ความเสี่ยง"].astype("string")
    )

    export_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # Create standardization report
    report = {
        "input_file": str(INPUT_FILE),
        "output_file": str(OUTPUT_FILE),
        "original_rows": original_rows,
        "output_rows": len(export_df),
        "rows_removed": original_rows - len(export_df),
        "risk_category_order": RISK_ORDER,
        "risk_categories_found": [
            str(value)
            for value in df["ความเสี่ยง"].cat.categories
            if value in df["ความเสี่ยง"].values
        ],
        "transformations": [
            "Defined an ordered risk category from very low to very high",
            "Verified the year column is integer",
            "Preserved original column names and missing values",
            "No rows were removed"
        ]
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\n===== STANDARDIZATION COMPLETED =====")
    print(f"Input rows: {original_rows}")
    print(f"Output rows: {len(export_df)}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Report file: {REPORT_FILE}")


if __name__ == "__main__":
    main()
