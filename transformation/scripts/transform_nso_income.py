from pathlib import Path
import json
import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "ingestion/data/Salary.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "transformation/output"
REPORT_DIR = PROJECT_ROOT / "transformation/reports"

CSV_OUTPUT = OUTPUT_DIR / "nso_household_income_transformed.csv"
PARQUET_OUTPUT = OUTPUT_DIR / "nso_household_income_transformed.parquet"
REPORT_OUTPUT = REPORT_DIR / "nso_household_income_transformation_report.json"


def transform_data():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Read source data
    df = pd.read_csv(INPUT_FILE)

    original_rows = len(df)
    original_columns = df.columns.tolist()

    # Standardize column names
    df.columns = df.columns.str.strip()

    # Clean text columns
    text_columns = df.select_dtypes(include=["object", "string"]).columns

    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()
        df[column] = df[column].replace("", pd.NA)

    # Convert year to nullable integer
    df["year"] = pd.to_numeric(
        df["year"], errors="coerce"
    ).astype("Int64")

    # Convert income value to numeric
    df["value"] = pd.to_numeric(
        df["value"], errors="coerce"
    )

    # Preserve missing values and actual zero values
    # Do not aggregate income categories

    # Save transformed data
    df.to_csv(CSV_OUTPUT, index=False, encoding="utf-8-sig")
    df.to_parquet(PARQUET_OUTPUT, index=False)

    # Create transformation report
    report = {
        "source_file": str(INPUT_FILE.relative_to(PROJECT_ROOT)),
        "output_csv": str(CSV_OUTPUT.relative_to(PROJECT_ROOT)),
        "output_parquet": str(PARQUET_OUTPUT.relative_to(PROJECT_ROOT)),
        "original_rows": original_rows,
        "transformed_rows": len(df),
        "original_columns": original_columns,
        "transformed_columns": df.columns.tolist(),
        "rows_removed": original_rows - len(df),
        "missing_values": {
            column: int(count)
            for column, count in df.isna().sum().items()
        },
        "year_distribution": {
            str(year): int(count)
            for year, count in df["year"].value_counts().sort_index().items()
        },
        "notes": [
            "Text columns were stripped of leading and trailing whitespace.",
            "Year was converted to nullable integer.",
            "Income value was converted to numeric.",
            "Missing values were preserved.",
            "Zero and negative income values were preserved.",
            "Income categories were not aggregated.",
            "Income data represents socioeconomic groups, not individual households."
        ]
    }

    with open(REPORT_OUTPUT, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    print("NSO income transformation completed.")
    print(f"Rows: {original_rows} -> {len(df)}")
    print(f"CSV: {CSV_OUTPUT}")
    print(f"Parquet: {PARQUET_OUTPUT}")
    print(f"Report: {REPORT_OUTPUT}")


if __name__ == "__main__":
    transform_data()