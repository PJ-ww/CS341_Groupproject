from pathlib import Path
import json
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "ingestion/data/raw/pdpm/flood_relief/pdpm_affected_households.xlsx"
)

OUTPUT_DIR = PROJECT_ROOT / "transformation/output"
REPORT_DIR = PROJECT_ROOT / "transformation/reports"

CSV_OUTPUT = OUTPUT_DIR / "affected_households_summary_transformed.csv"
PARQUET_OUTPUT = OUTPUT_DIR / "affected_households_summary_transformed.parquet"
REPORT_OUTPUT = REPORT_DIR / "affected_households_summary_transformation_report.json"


def transform_data():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Read source Excel
    df = pd.read_excel(INPUT_FILE, sheet_name="Sheet2")

    original_rows = len(df)
    original_columns = df.columns.tolist()

    # Standardize column names
    df.columns = df.columns.str.strip()

    # Clean text columns
    text_columns = df.select_dtypes(include=["object", "string"]).columns

    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()
        df[column] = df[column].replace("", pd.NA)

    # Convert household and affected-area counts to nullable integers
    df["จำนวน"] = pd.to_numeric(
        df["จำนวน"], errors="coerce"
    ).astype("Int64")

    # Preserve the original event round as text
    # Do not create a year because the source does not specify one

    # Save transformed data
    df.to_csv(
        CSV_OUTPUT,
        index=False,
        encoding="utf-8-sig"
    )

    df.to_parquet(
        PARQUET_OUTPUT,
        index=False
    )

    # Create transformation report
    report = {
        "source_file": str(INPUT_FILE.relative_to(PROJECT_ROOT)),
        "source_sheet": "Sheet2",
        "output_csv": str(CSV_OUTPUT.relative_to(PROJECT_ROOT)),
        "output_parquet": str(PARQUET_OUTPUT.relative_to(PROJECT_ROOT)),
        "original_rows": original_rows,
        "transformed_rows": len(df),
        "original_columns": original_columns,
        "transformed_columns": df.columns.tolist(),
        "rows_removed": original_rows - len(df),
        "item_distribution": {
            str(item): int(count)
            for item, count in df["รายการ"].value_counts().items()
        },
        "unit_distribution": {
            str(unit): int(count)
            for unit, count in df["หน่วยนับ"].value_counts().items()
        },
        "missing_values": {
            column: int(count)
            for column, count in df.isna().sum().items()
        },
        "duplicate_rows": int(df.duplicated().sum()),
        "notes": [
            "Text columns were stripped of leading and trailing whitespace.",
            "Count column was converted to nullable integer.",
            "Original event round was preserved.",
            "No year was created because the source does not specify one.",
            "Different measurement units were kept separate.",
            "No aggregation was performed across different units.",
            "Missing values were preserved.",
            "Original source file was not modified."
        ]
    }

    with open(REPORT_OUTPUT, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    print("Affected households summary transformation completed.")
    print(f"Rows: {original_rows} -> {len(df)}")
    print(f"CSV: {CSV_OUTPUT}")
    print(f"Parquet: {PARQUET_OUTPUT}")
    print(f"Report: {REPORT_OUTPUT}")


if __name__ == "__main__":
    transform_data()