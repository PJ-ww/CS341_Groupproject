
from pathlib import Path
import pandas as pd
import json


# PATH CONFIGURATION

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "transformation"
    / "output"
    / "geographic_data_standardized.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "transformation" / "output"
REPORT_DIR = PROJECT_ROOT / "transformation" / "reports"

OUTPUT_FILE = OUTPUT_DIR / "geographic_data_features.csv"
REPORT_FILE = REPORT_DIR / "geographic_data_features_report.json"


# FEATURE CONFIGURATION

RISK_MAPPING = {
    "เสี่ยงต่ำมาก": 1,
    "เสี่ยงต่ำ": 2,
    "เสี่ยงปานกลาง": 3,
    "เสี่ยงสูง": 4,
    "เสี่ยงสูงมาก": 5
}

RISK_LEVEL_MAPPING = {
    1: "Very Low",
    2: "Low",
    3: "Moderate",
    4: "High",
    5: "Very High"
}


# MAIN FUNCTION

def main():

    print("===== FEATURE ENGINEERING STARTED =====")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Read standardized data
    df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8-sig",
        dtype={"ปี": "Int64", "หมู่ที่": "Int64"}
    )

    original_rows = len(df)

    # Check required column
    if "ความเสี่ยง" not in df.columns:
        raise ValueError("Missing required column: ความเสี่ยง")

    # Check unknown risk categories
    unknown_risks = sorted(
        set(df["ความเสี่ยง"].dropna().unique())
        - set(RISK_MAPPING.keys())
    )

    if unknown_risks:
        raise ValueError(
            f"Unknown risk categories: {unknown_risks}"
        )

    # Create risk level code
    df["risk_level_code"] = (
        df["ความเสี่ยง"].map(RISK_MAPPING).astype("Int64")
    )

    # Create risk level in English
    df["risk_level"] = (
        df["risk_level_code"].map(RISK_LEVEL_MAPPING)
    )

    # Check feature generation
    if df["risk_level_code"].isnull().any():
        raise ValueError("Some risk levels could not be mapped")

    if df["risk_level"].isnull().any():
        raise ValueError("Some risk levels could not be translated")

    # Export feature dataset
    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # Create feature summary
    risk_code_counts = {
        str(int(key)): int(value)
        for key, value in df["risk_level_code"]
        .value_counts().sort_index().items()
    }

    risk_level_counts = {
        str(key): int(value)
        for key, value in df["risk_level"]
        .value_counts().items()
    }

    # Create report
    report = {
        "input_file": str(INPUT_FILE),
        "output_file": str(OUTPUT_FILE),
        "original_rows": original_rows,
        "output_rows": len(df),
        "rows_removed": original_rows - len(df),
        "features_created": {
            "risk_level_code": RISK_MAPPING,
            "risk_level": RISK_LEVEL_MAPPING
        },
        "risk_code_counts": risk_code_counts,
        "risk_level_counts": risk_level_counts,
        "transformations": [
            "Mapped Thai risk categories to numeric risk codes",
            "Translated risk levels into five unique English categories",
            "Preserved all original columns",
            "Preserved missing values in original columns",
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

    print("\n===== FEATURE ENGINEERING COMPLETED =====")
    print(f"Input rows: {original_rows}")
    print(f"Output rows: {len(df)}")
    print("Features created: risk_level_code, risk_level")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Report file: {REPORT_FILE}")


if __name__ == "__main__":
    main()
