
from pathlib import Path
import json

import pandas as pd


# Project paths
ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "ingestion/data/raw/pdpm/flood_stats/"
    / "pdpm_flood_village_stats.xlsx"
)

OUTPUT_DIR = ROOT / "transformation/output"
REPORT_DIR = ROOT / "transformation/reports"

OUTPUT_CSV = OUTPUT_DIR / "flood_village_stats_transformed.csv"
OUTPUT_PARQUET = OUTPUT_DIR / "flood_village_stats_transformed.parquet"
REPORT_FILE = REPORT_DIR / "flood_village_stats_transformation_report.json"

SHEET_NAME = "_SELECT_PROVINCE_CODE_PROVINCE_"

YEAR_COLUMNS = [
    "Y2562", "Y2563", "Y2564",
    "Y2565", "Y2566", "Y2567"
]

CODE_COLUMNS = [
    "PROVINCE_CODE",
    "AMPHUR_CODE",
    "DISTRICT_CODE",
    "MOO_NO",
    "ORG_CODE",
    "MOO_ID",
]

TEXT_COLUMNS = [
    "PROVINCE_NAME",
    "AMPHUR_NAME",
    "DISTRICT_NAME",
    "ORG_NAME",
    "COMMUNITY_NAME",
    "DIS_TYPE_NAME",
]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Read source data without modifying the original file
    df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)

    original_rows = len(df)
    original_columns = list(df.columns)

    # Normalize column names
    column_mapping = {
        str(column): str(column).strip()
        for column in df.columns
    }

    df = df.rename(columns=column_mapping)

    # Normalize text columns and preserve missing values
    for column in TEXT_COLUMNS:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
                .replace("", pd.NA)
            )

    # Preserve area codes as strings
    for column in CODE_COLUMNS:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
                .replace("", pd.NA)
            )

    # Convert yearly values to nullable integers
    for column in YEAR_COLUMNS:
        values = df[column].astype("string").str.strip()
        values = values.replace("", pd.NA)

        numeric_values = pd.to_numeric(values, errors="coerce")

        invalid_mask = values.notna() & numeric_values.isna()

        if invalid_mask.any():
            invalid_values = values[invalid_mask].unique().tolist()
            raise ValueError(
                f"Unexpected non-numeric values in {column}: "
                f"{invalid_values[:10]}"
            )

        non_integer_mask = (
            numeric_values.notna()
            & (numeric_values % 1 != 0)
        )

        if non_integer_mask.any():
            raise ValueError(
                f"Non-integer values found in {column}"
            )

        df[column] = numeric_values.astype("Int64")

    # Feature engineering
    df["years_with_reported_value"] = (
        df[YEAR_COLUMNS].notna().sum(axis=1).astype("Int64")
    )

    # Export transformed data
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    df.to_parquet(OUTPUT_PARQUET, index=False)

    # Transformation report
    report = {
        "input_file": str(INPUT_FILE.relative_to(ROOT)),
        "input_status": (
            "Raw source used because a separate Accepted file "
            "was not available locally; see validation report."
        ),
        "sheet_name": SHEET_NAME,
        "output_rows": len(df),
        "input_rows": original_rows,
        "rows_removed": original_rows - len(df),
        "original_columns": original_columns,
        "column_mapping": column_mapping,
        "year_columns": YEAR_COLUMNS,
        "code_columns": CODE_COLUMNS,
        "year_missing_counts": {
            column: int(df[column].isna().sum())
            for column in YEAR_COLUMNS
        },
        "feature_created": {
            "years_with_reported_value": {
                "description": (
                    "Number of year columns containing a reported value"
                ),
                "minimum": int(df["years_with_reported_value"].min()),
                "maximum": int(df["years_with_reported_value"].max()),
            }
        },
        "output_files": [
            str(OUTPUT_CSV.relative_to(ROOT)),
            str(OUTPUT_PARQUET.relative_to(ROOT)),
        ],
        "notes": [
            "No source rows were intentionally removed.",
            "Blank yearly values remain missing, not zero.",
            "Area codes are stored as strings.",
            "Text columns are normalized to string type.",
            "Original column names are recorded in column_mapping.",
            "The feature counts reported yearly values, not flood events."
        ]
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    print("Transformation completed.")
    print(f"Input rows: {original_rows}")
    print(f"Output rows: {len(df)}")
    print(f"Rows removed: {original_rows - len(df)}")
    print(f"CSV: {OUTPUT_CSV}")
    print(f"Parquet: {OUTPUT_PARQUET}")
    print(f"Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
