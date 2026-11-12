
# Data Transformation & Processing

## 1. Overview

This module transforms validated source datasets into standardized formats suitable for data storage and further analysis.

The transformation process includes:
- Data cleaning and standardization
- Data type conversion
- Missing value handling
- Feature engineering
- Data preparation for integration and storage
- Exporting transformed datasets in CSV and Parquet formats
- Generating transformation reports

## 2. Responsibilities

- Clean and standardize source datasets.
- Convert columns into appropriate data types.
- Preserve missing values according to source meaning.
- Create additional features when necessary.
- Integrate datasets only when geographic, temporal, and data-granularity compatibility is established.
- Prepare transformed datasets for the Data Storage module.

## 3. Directory Structure

```text
transformation/
├── scripts/
│   ├── clean_data.py
│   ├── standardize.py
│   ├── create_features.py
│   ├── transform_flood_village_stats.py
│   ├── transform_nso_income.py
│   ├── transform_disaster_budget.py
│   ├── transform_flood_affected_households.py
│   ├── transform_affected_households_summary.py
│   └── integrate_data.py
│
├── output/
│   ├── geographic_data_cleaned.csv
│   ├── geographic_data_standardized.csv
│   ├── geographic_data_features.csv
│   ├── flood_village_stats_transformed.csv
│   ├── flood_village_stats_transformed.parquet
│   ├── nso_household_income_transformed.csv
│   ├── nso_household_income_transformed.parquet
│   ├── disaster_budget_2564_transformed.csv
│   ├── disaster_budget_2564_transformed.parquet
│   ├── flood_affected_households_transformed.csv
│   ├── flood_affected_households_transformed.parquet
│   ├── affected_households_summary_transformed.csv
│   └── affected_households_summary_transformed.parquet
│
├── reports/
│   ├── geographic_data_cleaning_report.json
│   ├── geographic_data_standardization_report.json
│   ├── geographic_data_features_report.json
│   ├── flood_village_stats_transformation_report.json
│   ├── nso_household_income_transformation_report.json
│   ├── disaster_budget_2564_transformation_report.json
│   ├── flood_affected_households_transformation_report.json
│   └── affected_households_summary_transformation_report.json
│
└── README.md
```

## 4. Input Datasets

The module uses source datasets that have been checked by the Data Validation process.

| Dataset | Input File (local path) | S3 key | Source |
|---|---|---|---|
| Geographic Data | `validation/cleaned/Geographic_Data_deduplicated.csv` (committed) | `validation/batch_id=<id>/cleaned/...` | PDPM |
| Flood Village Stats | `ingestion/data/STATISTIC_FLD.xlsx` | `raw/pdpm/flood_stats/pdpm_flood_village_stats.xlsx` | PDPM |
| Household Income | `ingestion/data/Salary.csv` | `raw/nso/nso_household_income.csv` | NSO |
| Disaster Budget | `ingestion/data/2564_by_disaster_type1.csv` | `raw/pdpm/flood_stats/pdpm_2564_by_disaster_type.csv` | PDPM |
| Flood Affected Households | `ingestion/data/Number_of Households_Affected_by_Flooding.csv` | `raw/pdpm/flood_relief/pdpm_flood_affected_households.csv` | PDPM |
| Affected Households Summary | `ingestion/data/Number_of_Affected_Households.xlsx` | `raw/pdpm/flood_relief/pdpm_affected_households.xlsx` | PDPM |

Raw files are not stored in Git. Download them into `ingestion/data/` first, either from S3 or from the original sources (see [`ingestion/README.md`](../ingestion/README.md), sections 6 and 6B). The file names follow `local_file` in [`ingestion/config.py`](../ingestion/config.py).

Note:
- Geographic Data uses the deduplicated output from Data Validation.
- Flood Village Stats uses the raw Excel file because a separate accepted output was not available locally. Its Validation Report indicates that all 57,024 rows were accepted.
- The other listed datasets were confirmed as accepted in the Validation Report. Their raw inputs were used because separate accepted output files were not available locally.

## 5. Transformation Processes

### 5.1 Geographic Data

Scripts:
- `clean_data.py`
- `standardize.py`
- `create_features.py`

Processing:
- Removed leading and trailing whitespace.
- Standardized data types and risk categories.
- Created `risk_level_code`.
- Created `risk_level`.

Output:
- `geographic_data_cleaned.csv`
- `geographic_data_standardized.csv`
- `geographic_data_features.csv`

Results:
- Input rows: 1,772
- Output rows: 1,772
- Rows removed during transformation: 0
- Final output columns: 9

### 5.2 Flood Village Stats

Script:
- `transform_flood_village_stats.py`

Processing:
- Standardized column names.
- Converted text columns to String.
- Preserved area codes as String.
- Converted yearly columns `Y2562–Y2567` to nullable integers.
- Preserved missing yearly values.
- Created `years_with_reported_value`.

Output:
- `flood_village_stats_transformed.csv`
- `flood_village_stats_transformed.parquet`

Results:
- Input rows: 57,024
- Output rows: 57,024
- Rows removed: 0
- Output columns: 19

### 5.3 NSO Household Income

Script:
- `transform_nso_income.py`

Processing:
- Standardized text columns.
- Converted `year` to nullable integer.
- Converted `value` to numeric.
- Preserved zero and negative values.
- Preserved missing values in `attribute`.
- Did not aggregate income categories.

Output:
- `nso_household_income_transformed.csv`
- `nso_household_income_transformed.parquet`

Results:
- Input rows: 15,400
- Output rows: 15,400
- Rows removed: 0
- Output columns: 11

Important limitation:
- Income data is categorized by socioeconomic groups at province level.
- It does not represent individual household income.
- Yasothon has 100 records in year 2568, but these records represent different income categories and socioeconomic groups.

### 5.4 Disaster Budget 2564

Script:
- `transform_disaster_budget.py`

Processing:
- Selected province records from section 1 (วงเงินจังหวัด).
- Excluded summary rows and records outside section 1.
- Removed commas before numeric conversion.
- Converted dash values (`-` and `--`) to missing values.
- Added Buddhist year 2564.
- Preserved province-level budget information.

Output:
- `disaster_budget_2564_transformed.csv`
- `disaster_budget_2564_transformed.parquet`

Results:
- Original rows: 83
- Transformed rows: 76
- Province count: 76
- Rows excluded: 7
- Output columns: 17

Important limitation:
- This dataset represents province-level budget information for year 2564.
- Bangkok from section 2 and non-province summary records are excluded.

### 5.5 Flood Affected Households

Script:
- `transform_flood_affected_households.py`

Processing:
- Standardized text values.
- Converted year and household count to nullable integers.
- Preserved zero values and missing values.
- Did not aggregate records across geographic areas.

Output:
- `flood_affected_households_transformed.csv`
- `flood_affected_households_transformed.parquet`

Results:
- Input rows: 144
- Output rows: 144
- Rows removed: 0
- Output columns: 7

Important limitation:
- This dataset contains flood-affected household records from Phang Nga province.
- It is geographically different from the Yasothon Geographic Data.

### 5.6 Affected Households Summary

Script:
- `transform_affected_households_summary.py`

Processing:
- Read data from Excel sheet `Sheet2`.
- Standardized text columns.
- Converted `จำนวน` to nullable integer.
- Preserved event rounds and original measurement units.
- Did not aggregate different measurement units.
- Did not create a year because the source does not specify one.

Output:
- `affected_households_summary_transformed.csv`
- `affected_households_summary_transformed.parquet`

Results:
- Input rows: 48
- Output rows: 48
- Rows removed: 0
- Output columns: 5

Important limitation:
- The dataset contains three different measurement units:
  - ตำบล
  - หมู่บ้าน
  - ครัวเรือน
- Values must be interpreted separately according to their measurement units.

## 6. Integration Considerations

Datasets should only be joined when their geographic level, time period, and data granularity are compatible.

Current considerations:

- Geographic Data contains subdistrict and village-level risk information for Yasothon.
- NSO Household Income contains province-level socioeconomic group information. A province-year contextual relationship may be explored for Yasothon in 2568, but it must not be interpreted as household-level income.
- Disaster Budget contains province-level data for 2564. It can be used for province-level analysis when geographic and temporal limitations are documented.
- Flood Affected Households contains data from Phang Nga and should not be joined directly with Yasothon Geographic Data.
- Affected Households Summary contains district-level information and multiple measurement units. Its year and geographic compatibility must be established before integration.
- `pdpm_gd015.csv` overlaps with Flood Village Stats and does not provide additional non-missing yearly values for matching records. It is not used as a supplementary source.

No primary integrated fact table has been created yet. Integration keys and relationships must be confirmed before joining datasets.

## 7. Data Quality and Limitations

- Original raw files are not modified.
- Missing values are preserved when they represent unavailable or unreported information.
- Zero values are preserved when they are actual reported values.
- Dash values in the budget dataset are treated as missing, not zero.
- Income categories are not aggregated into household-level income.
- Different measurement units are not summed together.
- Geographic and temporal mismatches must be documented before integration.
- Transformation reports record row counts, missing values, and transformation details.

## 8. How to Run

Run commands from the repository root directory.

```bash
python transformation/scripts/clean_data.py
python transformation/scripts/standardize.py
python transformation/scripts/create_features.py
python transformation/scripts/transform_flood_village_stats.py
python transformation/scripts/transform_nso_income.py
python transformation/scripts/transform_disaster_budget.py
python transformation/scripts/transform_flood_affected_households.py
python transformation/scripts/transform_affected_households_summary.py
python transformation/scripts/integrate_data.py   # needs create_features.py and transform_nso_income.py outputs
```

Requires `pandas`, `pyarrow` and `openpyxl` (`python -m pip install -r requirements.txt`). The first three scripts only need the committed `validation/cleaned/` file; the `transform_*.py` scripts need the raw files in `ingestion/data/`.

## 9. Output Formats

- CSV: Suitable for inspection and data exchange.
- Parquet: Suitable for analytical processing and data storage.
- JSON: Transformation reports containing processing results and data quality information.

## 10. Tools

- Python
- Pandas
- PyArrow
- Boto3 (for AWS S3 integration when required)
