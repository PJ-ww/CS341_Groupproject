
"""Transform Chiang Mai flood datasets for 2566 and 2567.

Input:
    validation/cleaned/flood_2566_cleaned.csv
    validation/cleaned/flood_2567_cleaned.csv

Output:
    transformation/output/flood_2566_transformed.csv
    transformation/output/flood_2567_transformed.csv
    transformation/output/flood_chiangmai_combined.csv
    transformation/reports/flood_transformation_report.json
"""

import json
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = ROOT / "validation" / "cleaned"
OUTPUT_DIR = ROOT / "transformation" / "output"
REPORT_DIR = ROOT / "transformation" / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. Standard column mapping
# --------------------------------------------------

COLUMN_MAPPING = {
    # General information
    "event_name": {
        2566: "Incident Name",
        2567: "Situation name",
    },
    "disaster_type": {
        2566: "Incident Name",
        2567: "Disaster Type",
    },
    "disaster_date": {
        2566: "Disaster Date",
        2567: "Disaster Date",
    },

    # Geographic information
    "region": {
        2566: None,
        2567: "region",
    },
    "province_code": {
        2566: "Province Code",
        2567: "Province Code",
    },
    "province": {
        2566: "Province",
        2567: "Province",
    },
    "district_code": {
        2566: "District Code",
        2567: "District Code",
    },
    "district": {
        2566: "District",
        2567: "District",
    },
    "subdistrict_code": {
        2566: "Subdistrict Code",
        2567: "Sub-district Code",
    },
    "subdistrict": {
        2566: "Subdistrict",
        2567: "Sub-district",
    },
    "moo": {
        2566: "Moo",
        2567: "Moo",
    },
    "municipal_code": {
        2566: "Municipal Code",
        2567: "Municipal Code",
    },
    "municipality": {
        2566: "Municipality",
        2567: "Municipality",
    },
    "community": {
        2566: "Community",
        2567: "Community",
    },
    "village_code": {
        2566: "Village Code",
        2567: "Village Code",
    },

    # Additional information
    "zone_center": {
        2566: "Zone Center Name",
        2567: "District Center",
    },
    "cause": {
        2566: "Cause",
        2567: "Nature/Cause",
    },
    "title": {
        2566: None,
        2567: "Title",
    },
    "event_status": {
        2566: None,
        2567: "status",
    },
    "situation_status": {
        2566: None,
        2567: "situation",
    },

    # Dates with distinct source meanings
    "relief_declared_date": {
        2566: "Relief Declared Date",
        2567: None,
    },
    "disaster_area_date": {
        2566: "Disaster Area Date",
        2567: None,
    },
    "other_announce_date": {
        2566: "Other Announce Date",
        2567: None,
    },
    "end_disaster_date": {
        2566: "End Disaster Date",
        2567: None,
    },
    "aid_zone_declaration_date": {
        2566: None,
        2567: "Aid Zone Declaration",
    },
    "disaster_declaration_date": {
        2566: None,
        2567: "Disaster Declaration",
    },
    "other_declarations_date": {
        2566: None,
        2567: "Other Declarations",
    },
    "situation_ended_date": {
        2566: None,
        2567: "Situation Ended",
    },

    # Impact metrics
    "affected_people": {
        2566: "Affected People",
        2567: "Affected People",
    },
    "affected_households": {
        2566: "Affected Households",
        2567: "Affected Households",
    },
    "evacuated_people": {
        2566: "Evacuated People",
        2567: "Evacuees",
    },
    "evacuated_households": {
        2566: "Evacuated Households",
        2567: "Evacuees (Households)",
    },
    "deaths": {
        2566: "Deaths",
        2567: "fatalities_count",
    },
    "missing": {
        2566: "Missing",
        2567: "Missing Persons",
    },
    "injured": {
        2566: "Injured",
        2567: "injuries_count",
    },
    "housing_damage": {
        2566: "Housing Damage",
        2567: "Housing (Units)",
    },
    "business_damage": {
        2566: "Business Damage",
        2567: "Business (Sites)",
    },
    "agriculture_damage": {
        2566: "Agriculture Damage",
        2567: "Agriculture (Acres)",
    },
    "livestock_damage": {
        2566: "Livestock Damage",
        2567: "Livestock (Head)",
    },
    "fishing_damage": {
        2566: "Fishing Damage",
        2567: "Fisheries (Ponds)",
    },
    "transport_damage": {
        2566: "Transport Damage",
        2567: "Transportation (Sites)",
    },
    "health_damage": {
        2566: "Health Damage",
        2567: "Health (Sites)",
    },
    "culture_damage": {
        2566: "Culture Damage",
        2567: "Religion/Culture (Sites)",
    },
    "education_sports_damage": {
        2566: "Education/Sports",
        2567: "Education/Sports (Sites)",
    },
    "utilities_damage": {
        2566: "Utilities Damage",
        2567: "Utilities (Sites)",
    },
    "government_locations_damage": {
        2566: "Govt. Locations Damage",
        2567: "Government Sites",
    },
    "other_public_benefits_damage": {
        2566: "Other Public Benefits",
        2567: "Other Public Benefit (Sites)",
    },
    "government_property_damage": {
        2566: "Govt Property Damage",
        2567: "Gov./Private Property (Units)",
    },
}


DATE_COLUMNS = [
    "disaster_date",
    "relief_declared_date",
    "disaster_area_date",
    "other_announce_date",
    "end_disaster_date",
    "aid_zone_declaration_date",
    "disaster_declaration_date",
    "other_declarations_date",
    "situation_ended_date",
]


NUMERIC_COLUMNS = [
    "moo",
    "affected_people",
    "affected_households",
    "evacuated_people",
    "evacuated_households",
    "deaths",
    "missing",
    "injured",
    "housing_damage",
    "business_damage",
    "agriculture_damage",
    "livestock_damage",
    "fishing_damage",
    "transport_damage",
    "health_damage",
    "culture_damage",
    "education_sports_damage",
    "utilities_damage",
    "government_locations_damage",
    "other_public_benefits_damage",
    "government_property_damage",
]


TEXT_COLUMNS = [
    column
    for column in COLUMN_MAPPING
    if column not in NUMERIC_COLUMNS
    and column not in DATE_COLUMNS
]


# --------------------------------------------------
# 3. Helper functions
# --------------------------------------------------

def clean_text(series):
    """Trim whitespace while preserving missing values."""
    result = series.astype("string").str.strip()
    return result.replace("", pd.NA)


def parse_date(series, year):
    """Convert source dates to YYYY-MM-DD."""
    cleaned = clean_text(series)

    parsed = pd.to_datetime(
        cleaned,
        errors="coerce",
        dayfirst=(year == 2566),
    )

    return parsed.dt.strftime("%Y-%m-%d").astype("string")


def transform_one_year(year):
    """Transform one flood dataset."""

    input_file = INPUT_DIR / f"flood_{year}_cleaned.csv"

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_file}"
        )

    df = pd.read_csv(input_file, dtype=str)

    original_rows = len(df)

    # Keep only Chiang Mai province.
    province_code = clean_text(df["Province Code"])

    df = df.loc[
        province_code == "50"
    ].copy()

    chiangmai_rows = len(df)

    # Preserve original source row number.
    source_row_numbers = df.index + 1

    # Create standardized output.
    output = pd.DataFrame(index=df.index)

    output["source_year"] = year

    if year == 2567 and "_id" in df.columns:
        output["source_record_id"] = clean_text(df["_id"])
        output["source_record_id_type"] = "original"
    else:
        output["source_record_id"] = (
            "row-" + source_row_numbers.astype(str).str.zfill(6)
        )
        output["source_record_id_type"] = "generated_from_source_row"

    # Standardize column names.
    for target_column, source_columns in COLUMN_MAPPING.items():

        source_column = source_columns[year]

        if source_column is None:
            output[target_column] = pd.NA

        elif source_column not in df.columns:
            raise KeyError(
                f"Missing column '{source_column}' "
                f"in flood dataset {year}"
            )

        else:
            output[target_column] = df[source_column]

    # Clean text columns.
    for column in TEXT_COLUMNS:
        output[column] = clean_text(output[column])

    # Keep geographic codes as strings.
    code_columns = [
        "province_code",
        "district_code",
        "subdistrict_code",
        "municipal_code",
        "village_code",
    ]

    for column in code_columns:
        output[column] = clean_text(output[column])

    # Convert dates.
    date_conversion_errors = {}

    for column in DATE_COLUMNS:
        original = clean_text(output[column])

        parsed = parse_date(original, year)

        invalid_count = int(
            (original.notna() & parsed.isna()).sum()
        )

        date_conversion_errors[column] = invalid_count

        output[column] = parsed

    # Convert numeric columns without replacing missing values with zero.
    numeric_conversion_errors = {}

    for column in NUMERIC_COLUMNS:
        original = clean_text(output[column])

        numeric = pd.to_numeric(
            original.str.replace(",", "", regex=False),
            errors="coerce",
        )

        invalid_count = int(
            (original.notna() & numeric.isna()).sum()
        )

        numeric_conversion_errors[column] = invalid_count

        output[column] = numeric

    # Reset row index.
    output = output.reset_index(drop=True)

    # Export year-specific result.
    output_file = (
        OUTPUT_DIR / f"flood_{year}_transformed.csv"
    )

    output.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig",
    )

    report = {
        "year": year,
        "input_file": input_file.name,
        "output_file": str(output_file.relative_to(ROOT)),
        "input_rows": original_rows,
        "chiangmai_rows": chiangmai_rows,
        "output_rows": len(output),
        "rows_removed_after_filter": original_rows - chiangmai_rows,
        "columns": len(output.columns),
        "missing_village_codes": int(
            output["village_code"].isna().sum()
        ),
        "unique_village_codes": int(
            output["village_code"].nunique()
        ),
        "date_conversion_errors": date_conversion_errors,
        "numeric_conversion_errors": numeric_conversion_errors,
        "missing_values": {
            column: int(output[column].isna().sum())
            for column in output.columns
        },
    }

    print(f"\n===== FLOOD {year} TRANSFORMATION =====")
    print("Input rows:", original_rows)
    print("Chiang Mai rows:", chiangmai_rows)
    print("Output rows:", len(output))
    print("Output columns:", len(output.columns))
    print("Missing Village Codes:", report["missing_village_codes"])
    print("Saved:", output_file)

    return output, report


# --------------------------------------------------
# 4. Main process
# --------------------------------------------------

def main():

    flood_2566, report_2566 = transform_one_year(2566)
    flood_2567, report_2567 = transform_one_year(2567)

    # Combine both years using the standardized schema.
    combined = pd.concat(
        [flood_2566, flood_2567],
        ignore_index=True,
    )

    combined_file = (
        OUTPUT_DIR / "flood_chiangmai_combined.csv"
    )

    combined.to_csv(
        combined_file,
        index=False,
        encoding="utf-8-sig",
    )

    # Transformation report.
    final_report = {
        "dataset": "Chiang Mai Flood Data",
        "description": (
            "Standardized flood records for Chiang Mai "
            "in Buddhist years 2566 and 2567."
        ),
        "filter": {
            "province_code": "50",
            "province": "เชียงใหม่",
        },
        "year_2566": report_2566,
        "year_2567": report_2567,
        "combined": {
            "output_file": str(combined_file.relative_to(ROOT)),
            "total_rows": len(combined),
            "total_columns": len(combined.columns),
            "rows_by_year": {
                str(year): int(count)
                for year, count in
                combined["source_year"].value_counts().sort_index().items()
            },
        },
    }

    report_file = (
        REPORT_DIR / "flood_transformation_report.json"
    )

    with open(report_file, "w", encoding="utf-8") as file:
        json.dump(
            final_report,
            file,
            ensure_ascii=False,
            indent=4,
        )

    print("\n===== COMBINED FLOOD DATA =====")
    print("Total rows:", len(combined))
    print("Total columns:", len(combined.columns))
    print("Rows by year:")
    print(
        combined["source_year"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nSaved combined dataset:", combined_file)
    print("Saved report:", report_file)

    # Basic row-count assertions.
    assert len(flood_2566) == report_2566["chiangmai_rows"]
    assert len(flood_2567) == report_2567["chiangmai_rows"]
    assert len(combined) == len(flood_2566) + len(flood_2567)

    print("\nTRANSFORMATION COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
