"""Integrate household income records with village mapping data.

Only uniquely matched village names are joined.
Ambiguous and unmatched income records are retained without mapping attributes.
"""

import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

INCOME_FILE = (
    ROOT / "transformation" / "output" / "household_income_transformed.csv"
)
MAPPING_FILE = (
    ROOT / "transformation" / "output" / "village_mapping_transformed.csv"
)

OUTPUT_DIR = ROOT / "transformation" / "output"
REPORT_DIR = ROOT / "transformation" / "reports"

OUTPUT_FILE = OUTPUT_DIR / "household_income_mapping_integrated.csv"
REPORT_FILE = REPORT_DIR / "household_income_mapping_integration_report.json"


def normalize_text(value):
    """Trim surrounding whitespace without removing meaningful parentheses."""
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_area(value):
    """Remove only the leading Thai word 'บ้าน' and preserve parentheses."""
    value = normalize_text(value)
    return re.sub(r"^บ้าน\s*", "", value).strip()


def create_location_key(district, subdistrict, area):
    """Create a conservative administrative location key."""
    return (
        normalize_text(district),
        normalize_text(subdistrict),
        normalize_area(area),
    )


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    income = pd.read_csv(INCOME_FILE, dtype=str)
    mapping = pd.read_csv(MAPPING_FILE, dtype=str)

    income_rows = len(income)
    mapping_rows = len(mapping)

    required_income = ["district", "subdistrict", "area"]
    required_mapping = [
        "district_name",
        "subdistrict_name",
        "village_name",
        "village_code",
    ]

    for column in required_income:
        if column not in income.columns:
            raise ValueError(f"Missing income column: {column}")

    for column in required_mapping:
        if column not in mapping.columns:
            raise ValueError(f"Missing mapping column: {column}")

    if mapping["village_code"].isna().any():
        raise ValueError("Mapping contains missing village codes.")

    if mapping["village_code"].duplicated().any():
        raise ValueError("Mapping village codes are not unique.")

    # Build matching keys while preserving meaningful parentheses.
    income["_location_key"] = [
        create_location_key(district, subdistrict, area)
        for district, subdistrict, area in zip(
            income["district"],
            income["subdistrict"],
            income["area"],
        )
    ]

    mapping["_location_key"] = [
        create_location_key(district, subdistrict, village)
        for district, subdistrict, village in zip(
            mapping["district_name"],
            mapping["subdistrict_name"],
            mapping["village_name"],
        )
    ]

    # Count mapping candidates for each location key.
    mapping_key_counts = mapping["_location_key"].value_counts()

    unique_keys = set(
        mapping_key_counts[mapping_key_counts == 1].index
    )
    ambiguous_keys = set(
        mapping_key_counts[mapping_key_counts > 1].index
    )

    income_keys = income["_location_key"]

    income["mapping_match_status"] = "unmatched"
    income.loc[income_keys.isin(ambiguous_keys), "mapping_match_status"] = (
        "ambiguous"
    )
    income.loc[income_keys.isin(unique_keys), "mapping_match_status"] = (
        "unique_match"
    )

    # Select only location keys that have exactly one mapping record.
    unique_mapping = mapping[
        mapping["_location_key"].isin(unique_keys)
    ].copy()

    mapping_columns = [
        "_location_key",
        "village_code",
        "district_code",
        "subdistrict_code",
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
        column
        for column in mapping_columns
        if column not in unique_mapping.columns
    ]

    if missing_mapping_columns:
        raise ValueError(
            f"Missing mapping columns: {missing_mapping_columns}"
        )

    unique_mapping = unique_mapping[mapping_columns].copy()
    # Rename mapping household count to avoid column name collision.
    unique_mapping = unique_mapping.rename(
    columns={"households": "mapping_households"}
)

    # Left join preserves every income record.
    integrated = income.merge(
        unique_mapping,
        on="_location_key",
        how="left",
        validate="many_to_one",
    )

    integrated = integrated.drop(columns=["_location_key"])

    # Count matching statuses.
    status_counts = integrated["mapping_match_status"].value_counts()

    unique_match_rows = int(status_counts.get("unique_match", 0))
    ambiguous_rows = int(status_counts.get("ambiguous", 0))
    unmatched_rows = int(status_counts.get("unmatched", 0))

    # Verify row preservation and status consistency.
    if len(integrated) != income_rows:
        raise AssertionError(
            f"Row count changed: income={income_rows}, "
            f"integrated={len(integrated)}"
        )

    if unique_match_rows + ambiguous_rows + unmatched_rows != income_rows:
        raise AssertionError("Mapping match status counts do not add up.")

    if integrated.loc[
        integrated["mapping_match_status"] != "unique_match",
        "village_code",
    ].notna().any():
        raise AssertionError(
            "Ambiguous or unmatched records unexpectedly have village codes."
        )

    # Save integrated dataset.
    integrated.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    report = {
        "dataset": "Household Income and Village Mapping Integration",
        "income_input": str(INCOME_FILE.relative_to(ROOT)),
        "mapping_input": str(MAPPING_FILE.relative_to(ROOT)),
        "output_file": str(OUTPUT_FILE.relative_to(ROOT)),
        "join_keys": [
            "district",
            "subdistrict",
            "area",
        ],
        "normalization_rules": [
            "Trim leading and trailing whitespace.",
            "Remove only the leading Thai word 'บ้าน' from area names.",
            "Preserve parentheses and their contents.",
            "Do not automatically correct spelling differences.",
        ],
        "join_type": "left",
        "matching_rule": (
            "Join only when the normalized location key matches "
            "exactly one mapping record."
        ),
        "income_input_rows": int(income_rows),
        "mapping_input_rows": int(mapping_rows),
        "output_rows": int(len(integrated)),
        "output_columns": int(len(integrated.columns)),
        "unique_match_rows": unique_match_rows,
        "ambiguous_rows": ambiguous_rows,
        "unmatched_rows": unmatched_rows,
        "unique_match_rate_percent": round(
            unique_match_rows / income_rows * 100, 2
        ) if income_rows else 0,
        "ambiguous_rate_percent": round(
            ambiguous_rows / income_rows * 100, 2
        ) if income_rows else 0,
        "unmatched_rate_percent": round(
            unmatched_rows / income_rows * 100, 2
        ) if income_rows else 0,
        "unique_matched_village_codes": int(
            integrated.loc[
                integrated["mapping_match_status"] == "unique_match",
                "village_code",
            ].nunique()
        ),
        "notes": [
            "Left join preserves all household income records.",
            "Only uniquely matched location keys receive mapping attributes.",
            "Ambiguous location keys are not arbitrarily assigned.",
            "Unmatched records are retained without mapping attributes.",
            "Duplicate income records are preserved.",
            "No mapping values are invented or filled.",
            "Household income data has no year field.",
            "Parenthetical text in area names is preserved.",
        ],
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=4)

    print("Household income and mapping integration completed.")
    print(f"Income input rows: {income_rows}")
    print(f"Mapping input rows: {mapping_rows}")
    print(f"Integrated rows: {len(integrated)}")
    print(f"Unique match rows: {unique_match_rows}")
    print(f"Ambiguous rows: {ambiguous_rows}")
    print(f"Unmatched rows: {unmatched_rows}")
    print(f"Unique match rate: {report['unique_match_rate_percent']}%")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
