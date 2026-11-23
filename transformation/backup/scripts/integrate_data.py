
from pathlib import Path
import json

import pandas as pd


# 1. Paths and configuration

TRANSFORMATION_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = TRANSFORMATION_DIR / "output"
REPORT_DIR = TRANSFORMATION_DIR / "reports"

GEOGRAPHIC_FILE = OUTPUT_DIR / "geographic_data_features.csv"
NSO_FILE = OUTPUT_DIR / "nso_household_income_transformed.csv"

OUTPUT_CSV = OUTPUT_DIR / "geographic_nso_integrated.csv"
OUTPUT_PARQUET = OUTPUT_DIR / "geographic_nso_integrated.parquet"
REPORT_FILE = REPORT_DIR / "geographic_nso_integration_report.json"

# Geographic dataset contains areas in Yasothon province.
GEOGRAPHIC_PROVINCE = "ยโสธร"
TARGET_YEAR = 2568
INCOME_CATEGORY = "รายได้ทั้งสิ้นต่อเดือน"


# 2. Load transformed datasets

def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    geographic = pd.read_csv(GEOGRAPHIC_FILE)
    nso = pd.read_csv(NSO_FILE)

    geographic_rows_before = len(geographic)
    nso_rows_before = len(nso)

    # Normalize join keys.
    geographic["ปี"] = pd.to_numeric(
        geographic["ปี"], errors="coerce"
    ).astype("Int64")

    nso["year"] = pd.to_numeric(
        nso["year"], errors="coerce"
    ).astype("Int64")

    nso["province"] = nso["province"].astype("string").str.strip()
    nso["source_income3"] = (
        nso["source_income3"].astype("string").str.strip()
    )

    # 3. Filter the same province and year

    geographic = geographic[
        geographic["ปี"] == TARGET_YEAR
    ].copy()

    # Add province from the known geographic source coverage.
    geographic["จังหวัด"] = GEOGRAPHIC_PROVINCE

    nso_selected = nso[
        (nso["year"] == TARGET_YEAR)
        & (nso["province"] == GEOGRAPHIC_PROVINCE)
        & (nso["source_income3"] == INCOME_CATEGORY)
    ].copy()

    if geographic.empty:
        raise ValueError(
            f"No Geographic Data found for year {TARGET_YEAR}"
        )

    if nso_selected.empty:
        raise ValueError(
            "No matching NSO income records found "
            "for Yasothon in 2568."
        )

    # 4. Aggregate Geographic risk data

    risk_counts = (
        geographic["risk_level"]
        .value_counts()
        .reindex(
            ["Very Low", "Low", "Moderate", "High", "Very High"],
            fill_value=0
        )
    )

    total_geographic_rows = len(geographic)

    geographic_summary = {
        "จังหวัด": GEOGRAPHIC_PROVINCE,
        "ปี": TARGET_YEAR,
        "geographic_area_records": total_geographic_rows,
    }

    for risk_level, count in risk_counts.items():
        column_name = (
            "risk_" + risk_level.lower().replace(" ", "_") + "_count"
        )
        geographic_summary[column_name] = int(count)

    for risk_level, count in risk_counts.items():
        column_name = (
            "risk_" + risk_level.lower().replace(" ", "_") + "_pct"
        )
        geographic_summary[column_name] = (
            round(float(count) / total_geographic_rows * 100, 2)
        )

    geographic_summary_df = pd.DataFrame([geographic_summary])

    # 5. Prepare NSO income records

    nso_selected = nso_selected.rename(
        columns={
            "year": "ปี",
            "province": "จังหวัด",
            "source_income3": "income_indicator",
            "soc_eco_class2": "socioeconomic_group",
            "value": "monthly_income_value",
            "unit": "income_unit",
        }
    )

    nso_selected = nso_selected[
        [
            "จังหวัด",
            "ปี",
            "income_indicator",
            "socioeconomic_group",
            "monthly_income_value",
            "income_unit",
        ]
    ].copy()


    # 6. Integrate at province-year level

    integrated = nso_selected.merge(
        geographic_summary_df,
        on=["จังหวัด", "ปี"],
        how="inner",
        validate="many_to_one"
    )

    if integrated.empty:
        raise ValueError("Integration produced no matching records.")

    # 7. Save integrated outputs

    integrated.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    integrated.to_parquet(OUTPUT_PARQUET, index=False)

    # 8. Create integration report

    report = {
        "process": "Geographic Data and NSO Income Integration",
        "join_keys": ["จังหวัด", "ปี"],
        "province": GEOGRAPHIC_PROVINCE,
        "year": TARGET_YEAR,
        "income_indicator": INCOME_CATEGORY,
        "geographic_rows_before_filter": geographic_rows_before,
        "nso_rows_before_filter": nso_rows_before,
        "geographic_rows_after_filter": total_geographic_rows,
        "nso_income_rows_after_filter": len(nso_selected),
        "integrated_rows": len(integrated),
        "geographic_risk_summary": {
            str(key): int(value)
            for key, value in risk_counts.items()
        },
        "join_type": "many NSO socioeconomic groups to one geographic summary",
        "join_validation": "many_to_one",
        "limitations": [
            "Geographic risk data is at subdistrict/village record level "
            "and is aggregated to province-year level before integration.",
            "NSO income data is provincial survey data separated by "
            "socioeconomic group, not individual household income.",
            "Geographic risk summary is repeated for each socioeconomic "
            "group in the integrated contextual dataset.",
            "This integration does not establish household-level "
            "relationships between income and flood risk."
        ],
        "outputs": [
            str(OUTPUT_CSV),
            str(OUTPUT_PARQUET),
        ],
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=4)

    print("Integration completed successfully.")
    print(f"Geographic rows: {total_geographic_rows}")
    print(f"NSO income groups: {len(nso_selected)}")
    print(f"Integrated rows: {len(integrated)}")
    print(f"CSV: {OUTPUT_CSV}")
    print(f"Parquet: {OUTPUT_PARQUET}")
    print(f"Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
