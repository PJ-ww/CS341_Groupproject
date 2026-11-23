"""Transform Chiang Mai village mapping data."""

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "validation"
    / "cleaned"
    / "village_mapping_cleaned.csv"
)

OUTPUT_DIR = ROOT / "transformation" / "output"
REPORT_DIR = ROOT / "transformation" / "reports"

OUTPUT_FILE = OUTPUT_DIR / "village_mapping_transformed.csv"
REPORT_FILE = REPORT_DIR / "village_mapping_transformation_report.json"


COLUMN_MAPPING = {
    "pcode": "province_code",
    "pname": "province_name",
    "tname": "subdistrict_name",
    "acode": "district_code",
    "aname": "district_name",
    "tcode": "subdistrict_code",
    "mcode": "village_code",
    "mname": "village_name",
    "oct_side15_lat": "latitude",
    "oct_side15_lon": "longitude",
    "oct_side15_distance": "distance",
    "oct_side15_road": "road_flag",
    "oct_side15_road_name": "road_name",
    "oct_side15_road_num": "road_number",
    "oct_side15_road_distance": "road_distance",
    "oct_side15_road_name2": "road_name_2",
    "oct_side15_road_num2": "road_number_2",
    "oct_side15_wmen": "women",
    "oct_side15_men": "men",
    "oct_side15_total": "population_total",
    "oct_side15_house": "households",
    "oct_side15_leader": "leader_flag",
    "oct_side15_leader_cause": "leader_cause",
    "oct_side15_local": "local_government_flag",
    "oct_side15_local_name": "local_government_name",
    "oct_side15_local2": "local_government_2_flag",
    "oct_side15_local2_name": "local_government_2_name",
    "oct_side15_local3": "local_government_3_flag",
    "oct_side15_local3_name": "local_government_3_name",
    "oct_side15_local4": "local_government_4_flag",
    "oct_side15_local4_name": "local_government_4_name",
    "oct_side15_local5": "local_government_5_flag",
    "oct_side15_local5_name": "local_government_5_name",
    "oct_side15_river": "river_flag",
    "oct_side15_river_name": "river_name",
    "oct_side15_sea": "sea_flag",
    "oct_side15_sea_name": "sea_name",
    "oct_side15_lagoon": "lagoon_flag",
    "oct_side15_lagoon_name": "lagoon_name",
    "oct_side15_mangrove": "mangrove_flag",
    "oct_side15_mangrove_name": "mangrove_name",
    "oct_side15_mangrove_area": "mangrove_area",
    "oct_side15_swamp": "swamp_flag",
    "oct_side15_swamp_name": "swamp_name",
    "oct_side15_swamp_area": "swamp_area",
    "oct_side15_island": "island_flag",
    "oct_side15_island_name": "island_name",
    "oct_side15_foth": "forest_flag",
    "oct_side15_foth_name": "forest_name",
    "oct_side15_mountain": "mountain_flag",
    "oct_side15_mountain_name": "mountain_name",
    "oct_side15_mountain_sea_leval": "mountain_elevation",
    "oct_side15_border": "border_flag",
    "oct_side15_border_name1": "border_name_1",
    "oct_side15_border_distance1": "border_distance_1",
    "oct_side15_border_name2": "border_name_2",
    "oct_side15_border_distance2": "border_distance_2",
    "oct_side15_mm_type1": "landform_type_1",
    "oct_side15_mm_type2": "landform_type_2",
    "oct_side15_mm_type2_name": "landform_type_2_name",
    "oct_side15_mm_type3": "landform_type_3",
    "oct_side15_mm_type3_name": "landform_type_3_name",
    "oct_side15_power": "electricity_flag",
    "oct_side15_power_name": "electricity_name",
    "oct_side15_highvoltage": "high_voltage_flag",
    "oct_side15_dam": "dam_flag",
    "oct_side15_dam_name": "dam_name",
    "oct_side15_reservoir": "reservoir_flag",
    "oct_side15_reservoir_name": "reservoir_name",
    "oct_side15_weir": "weir_flag",
    "oct_side15_weir_name": "weir_name",
    "oct_side15_housing": "housing_flag",
    "oct_side15_housing_total": "housing_total",
    "oct_side15_condos": "condominium_flag",
    "oct_side15_condos_total": "condominium_total",
}


ID_COLUMNS = [
    "province_code",
    "district_code",
    "subdistrict_code",
    "village_code",
]

TEXT_COLUMNS = [
    "province_name",
    "district_name",
    "subdistrict_name",
    "village_name",
    "road_name",
    "road_name_2",
    "leader_cause",
    "local_government_name",
    "local_government_2_name",
    "local_government_3_name",
    "local_government_4_name",
    "local_government_5_name",
    "river_name",
    "sea_name",
    "lagoon_name",
    "mangrove_name",
    "swamp_name",
    "island_name",
    "forest_name",
    "mountain_name",
    "border_name_1",
    "border_name_2",
    "landform_type_2_name",
    "landform_type_3_name",
    "electricity_name",
    "dam_name",
    "reservoir_name",
    "weir_name",
    "road_number",
    "road_number_2",
]

NUMERIC_COLUMNS = [
    column
    for column in COLUMN_MAPPING.values()
    if column not in ID_COLUMNS + TEXT_COLUMNS
]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE, dtype=str)

    input_rows = len(df)
    input_columns = len(df.columns)

    missing_columns = [
        column for column in COLUMN_MAPPING
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if len(COLUMN_MAPPING) != input_columns:
        raise ValueError(
            "Column mapping does not match the source column count."
        )

    transformed = df.rename(columns=COLUMN_MAPPING).copy()

    # Preserve administrative codes as strings.
    for column in ID_COLUMNS:
        transformed[column] = transformed[column].astype("string").str.strip()

    # Preserve names and labels without changing their spelling.
    for column in TEXT_COLUMNS:
        transformed[column] = transformed[column].astype("string").str.strip()

    # Convert numeric attributes while preserving missing values.
    numeric_errors = {}
    for column in NUMERIC_COLUMNS:
        original = transformed[column].copy()

        if column == "mountain_elevation":
            cleaned = original.str.replace(",", "", regex=False)
        else:
            cleaned = original

        converted = pd.to_numeric(cleaned, errors="coerce")
        invalid_mask = original.notna() & converted.isna()
        numeric_errors[column] = int(invalid_mask.sum())

        transformed[column] = converted

    # Check village codes and coordinates.
    missing_village_codes = int(
        transformed["village_code"].isna().sum()
    )

    duplicate_village_codes = int(
        transformed["village_code"].duplicated().sum()
    )

    missing_coordinates = int(
        transformed[["latitude", "longitude"]]
        .isna()
        .any(axis=1)
        .sum()
    )

    # Save the complete transformed dataset.
    transformed.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    report = {
        "dataset": "Chiang Mai Village Mapping",
        "input_file": str(INPUT_FILE.relative_to(ROOT)),
        "output_file": str(OUTPUT_FILE.relative_to(ROOT)),
        "input_rows": int(input_rows),
        "output_rows": int(len(transformed)),
        "input_columns": int(input_columns),
        "output_columns": int(len(transformed.columns)),
        "columns": list(transformed.columns),
        "province_codes": (
            transformed["province_code"]
            .value_counts(dropna=False)
            .to_dict()
        ),
        "missing_values": {
            column: int(transformed[column].isna().sum())
            for column in transformed.columns
        },
        "numeric_conversion_errors": numeric_errors,
        "missing_village_codes": missing_village_codes,
        "duplicate_village_codes": duplicate_village_codes,
        "unique_village_codes": int(
            transformed["village_code"].nunique(dropna=True)
        ),
        "missing_coordinate_rows": missing_coordinates,
        "district_count": int(
            transformed["district_code"].nunique(dropna=True)
        ),
        "subdistrict_count": int(
            transformed["subdistrict_code"].nunique(dropna=True)
        ),
        "notes": [
            "All source rows and columns are retained.",
            "Administrative codes are stored as strings.",
            "Numeric attributes are converted without filling missing values.",
            "Source names and spelling are preserved.",
            "Quarantined mapping records are not added.",
            "No flood or household income join is performed.",
        ],
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=4)

    print("Village mapping transformation completed.")
    print(f"Input shape: {input_rows} rows x {input_columns} columns")
    print(
        f"Output shape: {len(transformed)} rows x "
        f"{len(transformed.columns)} columns"
    )
    print(f"Missing village codes: {missing_village_codes}")
    print(f"Duplicate village codes: {duplicate_village_codes}")
    print(f"Missing coordinate rows: {missing_coordinates}")
    print(f"Numeric conversion errors: {numeric_errors}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
