
from pathlib import Path
import json
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "ingestion/data/raw/pdpm/flood_stats/pdpm_2564_by_disaster_type.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "transformation/output"
REPORT_DIR = PROJECT_ROOT / "transformation/reports"

CSV_OUTPUT = OUTPUT_DIR / "disaster_budget_2564_transformed.csv"
PARQUET_OUTPUT = OUTPUT_DIR / "disaster_budget_2564_transformed.parquet"
REPORT_OUTPUT = REPORT_DIR / "disaster_budget_2564_transformation_report.json"


def transform_data():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Read source as text to preserve original values
    df = pd.read_csv(INPUT_FILE, dtype="string")

    original_rows = len(df)

    # Remove whitespace from column names and text values
    df.columns = df.columns.str.strip()

    for column in df.columns:
        df[column] = df[column].str.strip()

    # Find the beginning of section 2
    section2_mask = df["ที่"].str.contains(
        r"2\.\s*วงเงินอำนาจอธิบดี",
        na=False,
        regex=True
    )

    if not section2_mask.any():
        raise ValueError("Cannot find section 2 in the source file.")

    section2_start = df.index[section2_mask][0]

    # Select only section 1: province budget
    section1 = df.loc[:section2_start - 1].copy()

    # Select actual province rows only
    province_rows = section1[
        section1["ที่"].str.fullmatch(r"\d+", na=False).fillna(False)
        & section1["จังหวัด"].notna()
    ].copy()

    selected_rows = len(province_rows)

    # Convert numeric columns
    numeric_columns = [
        column for column in province_rows.columns
        if column not in ["ที่", "จังหวัด"]
    ]

    for column in numeric_columns:
        province_rows[column] = (
            province_rows[column]
            .str.replace(",", "", regex=False)
            .replace({
                "-": pd.NA,
                "--": pd.NA,
                "": pd.NA
            })
        )

        province_rows[column] = pd.to_numeric(
            province_rows[column],
            errors="coerce"
        )

    # Standardize province number
    province_rows["ที่"] = province_rows["ที่"].astype("Int64")

    # Add source year
    province_rows["ปี"] = 2564

    # Reorder columns
    province_rows = province_rows[
        ["ปี"] + [
            column for column in province_rows.columns
            if column != "ปี"
        ]
    ]

    # Check province count
    province_count = int(province_rows["จังหวัด"].nunique())

    # Save transformed data
    province_rows.to_csv(
        CSV_OUTPUT,
        index=False,
        encoding="utf-8-sig"
    )

    province_rows.to_parquet(
        PARQUET_OUTPUT,
        index=False
    )

    # Create transformation report
    report = {
        "source_file": str(INPUT_FILE.relative_to(PROJECT_ROOT)),
        "output_csv": str(CSV_OUTPUT.relative_to(PROJECT_ROOT)),
        "output_parquet": str(PARQUET_OUTPUT.relative_to(PROJECT_ROOT)),
        "original_rows": original_rows,
        "transformed_rows": len(province_rows),
        "rows_excluded": original_rows - len(province_rows),
        "province_count": province_count,
        "year": 2564,
        "missing_values": {
            column: int(count)
            for column, count in province_rows.isna().sum().items()
        },
        "notes": [
            "Only province rows from section 1 (วงเงินจังหวัด) were selected.",
            "Summary rows and non-province rows were excluded.",
            "Commas were removed before numeric conversion.",
            "Dash values (- and --) were treated as missing, not zero.",
            "Original source data was not modified.",
            "The dataset represents province-level budget data for Buddhist year 2564."
        ]
    }

    with open(REPORT_OUTPUT, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    print("Disaster budget transformation completed.")
    print(f"Original rows: {original_rows}")
    print(f"Transformed rows: {len(province_rows)}")
    print(f"Province count: {province_count}")
    print(f"CSV: {CSV_OUTPUT}")
    print(f"Parquet: {PARQUET_OUTPUT}")
    print(f"Report: {REPORT_OUTPUT}")


if __name__ == "__main__":
    transform_data()
