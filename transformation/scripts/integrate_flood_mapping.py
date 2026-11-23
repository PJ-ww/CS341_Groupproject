"""Integrate Chiang Mai flood records with village mapping data."""

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

FLOOD_FILE = ROOT / "transformation" / "output" / "flood_chiangmai_combined.csv"
MAPPING_FILE = ROOT / "transformation" / "output" / "village_mapping_transformed.csv"

OUTPUT_DIR = ROOT / "transformation" / "output"
REPORT_DIR = ROOT / "transformation" / "reports"

OUTPUT_FILE = OUTPUT_DIR / "flood_mapping_integrated.csv"
REPORT_FILE = REPORT_DIR / "flood_mapping_integration_report.json"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    flood = pd.read_csv(FLOOD_FILE, dtype={"village_code": "string"})
    mapping = pd.read_csv(MAPPING_FILE, dtype={"village_code": "string"})

    flood_rows = len(flood)
    mapping_rows = len(mapping)

    required_flood = ["village_code"]
    required_mapping = ["village_code"]

    for column in required_flood:
        if column not in flood.columns:
            raise ValueError(f"Missing flood column: {column}")

    for column in required_mapping:
        if column not in mapping.columns:
            raise ValueError(f"Missing mapping column: {column}")

    if mapping["village_code"].isna().any():
        raise ValueError("Mapping contains missing village codes.")

    if mapping["village_code"].duplicated().any():
        raise ValueError("Mapping village codes are not unique.")

    if flood["village_code"].isna().any():
        raise ValueError("Flood contains missing village codes.")

    # Keep mapping attributes only; avoid duplicate administrative fields.
    mapping_columns = [
        "village_code",
        "village_name",
        "latitude",
        "longitude",
        "population_total",
        "women",
        "men",
        "households",
        "river_flag",
        "river_name",
        "mountain_flag",
        "mountain_name",
        "swamp_flag",
        "swamp_name",
        "dam_flag",
        "dam_name",
        "reservoir_flag",
        "reservoir_name",
    ]

    missing_mapping_columns = [
        column for column in mapping_columns
        if column not in mapping.columns
    ]

    if missing_mapping_columns:
        raise ValueError(
            f"Missing mapping columns: {missing_mapping_columns}"
        )

    mapping_subset = mapping[mapping_columns].copy()

    # Left join preserves every flood record.
    integrated = flood.merge(
        mapping_subset,
        on="village_code",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    integrated["mapping_match_status"] = integrated["_merge"].map(
        {
            "both": "matched",
            "left_only": "unmatched",
        }
    )

    integrated = integrated.drop(columns=["_merge"])

    matched_rows = int(
        (integrated["mapping_match_status"] == "matched").sum()
    )
    unmatched_rows = int(
        (integrated["mapping_match_status"] == "unmatched").sum()
    )

    # Verify row preservation.
    if len(integrated) != flood_rows:
        raise AssertionError(
            f"Row count changed: flood={flood_rows}, integrated={len(integrated)}"
        )

    # Save integrated dataset.
    integrated.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    report = {
        "dataset": "Flood and Village Mapping Integration",
        "flood_input": str(FLOOD_FILE.relative_to(ROOT)),
        "mapping_input": str(MAPPING_FILE.relative_to(ROOT)),
        "output_file": str(OUTPUT_FILE.relative_to(ROOT)),
        "join_key": "village_code",
        "join_type": "left",
        "validation": "many_to_one",
        "flood_input_rows": int(flood_rows),
        "mapping_input_rows": int(mapping_rows),
        "output_rows": int(len(integrated)),
        "output_columns": int(len(integrated.columns)),
        "matched_rows": matched_rows,
        "unmatched_rows": unmatched_rows,
        "match_rate_percent": round(
            matched_rows / flood_rows * 100, 2
        ) if flood_rows else 0,
        "unmatched_unique_village_codes": int(
            integrated.loc[
                integrated["mapping_match_status"] == "unmatched",
                "village_code",
            ].nunique()
        ),
        "notes": [
            "Left join preserves all flood records.",
            "Mapping village codes must be unique.",
            "Unmatched flood records are retained.",
            "No mapping values are invented or filled.",
            "Quarantined mapping records are not included.",
            "Only selected village mapping attributes are added.",
        ],
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=4)

    print("Flood and mapping integration completed.")
    print(f"Flood input rows: {flood_rows}")
    print(f"Mapping input rows: {mapping_rows}")
    print(f"Integrated rows: {len(integrated)}")
    print(f"Matched rows: {matched_rows}")
    print(f"Unmatched rows: {unmatched_rows}")
    print(f"Match rate: {report['match_rate_percent']}%")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
