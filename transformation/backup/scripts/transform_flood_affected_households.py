from pathlib import Path
import json
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "ingestion/data/raw/pdpm/flood_relief/pdpm_flood_affected_households.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "transformation/output"
REPORT_DIR = PROJECT_ROOT / "transformation/reports"

CSV_OUTPUT = OUTPUT_DIR / "flood_affected_households_transformed.csv"
PARQUET_OUTPUT = OUTPUT_DIR / "flood_affected_households_transformed.parquet"
REPORT_OUTPUT = REPORT_DIR / "flood_affected_households_transformation_report.json"


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

    # Convert year and household count to nullable integers
    df["ปี"] = pd.to_numeric(
        df["ปี"], errors="coerce"
    ).astype("Int64")

    df["จำนวน"] = pd.to_numeric(
        df["จำนวน"], errors="coerce"
    ).astype("Int64")

    # Preserve zero values and missing values
    # Do not aggregate across different geographic areas

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
        "output_csv": str(CSV_OUTPUT.relative_to(PROJECT_ROOT)),
        "output_parquet": str(PARQUET_OUTPUT.relative_to(PROJECT_ROOT)),
        "original_rows": original_rows,
        "transformed_rows": len(df),
        "original_columns": original_columns,
        "transformed_columns": df.columns.tolist(),
        "rows_removed": original_rows - len(df),
        "year_distribution": {
            str(year): int(count)
            for year, count in df["ปี"].value_counts().sort_index().items()
        },
        "unit_distribution": {
            str(unit): int(count)
            for unit, count in df["หน่วย"].value_counts(dropna=False).items()
        },
        "missing_values": {
            column: int(count)
            for column, count in df.isna().sum().items()
        },
        "duplicate_rows": int(df.duplicated().sum()),
        "notes": [
            "Column names and text values were stripped of whitespace.",
            "Year was converted to nullable integer.",
            "Household count was converted to nullable integer.",
            "Zero values were preserved.",
            "Missing values were preserved.",
            "No rows were removed.",
            "Data represents flood-affected households in Phang Nga province.",
            "Data was not joined with Yasothon geographic data because the geographic areas differ."
        ]
    }

    with open(REPORT_OUTPUT, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    print("Flood affected households transformation completed.")
    print(f"Rows: {original_rows} -> {len(df)}")
    print(f"CSV: {CSV_OUTPUT}")
    print(f"Parquet: {PARQUET_OUTPUT}")
    print(f"Report: {REPORT_OUTPUT}")


if __name__ == "__main__":
    transform_data()