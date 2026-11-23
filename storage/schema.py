"""Curated-zone table definitions (Person 4: Data Storage, Data Model & Query).

Each table lists its source file from transformation/output/, its grain, its
primary key and an explicit column type. build_curated.py enforces these types
when writing Parquet, and generate_ddl.py turns the same definitions into the
Athena DDL, so the files on S3 and the Glue catalog cannot drift apart.

Type names are the Athena/Hive names: string, int, bigint, double, date.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRANSFORM_OUT = ROOT / "transformation" / "output"
CURATED_DIR = ROOT / "storage" / "curated"
REPORT_DIR = ROOT / "storage" / "reports"

DATABASE = "flood_recovery_db"
BUCKET = "cs341-flood-recovery"
S3_PREFIX = "curated/"

# ---------------------------------------------------------------- dim_village
_VILLAGE_CODES = {
    "province_code": 2, "district_code": 4, "subdistrict_code": 6, "village_code": 8,
}
_VILLAGE_DOUBLE = [
    "latitude", "longitude", "distance", "road_distance", "swamp_area",
    "mountain_elevation", "border_distance_1",
]
_VILLAGE_BIGINT = [
    "women", "men", "population_total", "households", "housing_total", "condominium_total",
]
_VILLAGE_INT = ["landform_type_1", "landform_type_2", "landform_type_3"]


def _village_type(col):
    if col in _VILLAGE_CODES:
        return "string"
    if col in _VILLAGE_DOUBLE:
        return "double"
    if col in _VILLAGE_BIGINT:
        return "bigint"
    if col.endswith("_flag") or col in _VILLAGE_INT:
        return "int"
    return "string"


# --------------------------------------------------------- fact_flood_report
_FLOOD_COLUMNS = [
    ("source_record_id", "string"), ("source_record_id_type", "string"),
    ("event_name", "string"), ("disaster_type", "string"), ("disaster_date", "date"),
    ("region", "string"),
    ("province_code", "string"), ("province", "string"),
    ("district_code", "string"), ("district", "string"),
    ("subdistrict_code", "string"), ("subdistrict", "string"),
    ("moo", "int"), ("municipal_code", "string"), ("municipality", "string"),
    ("community", "string"), ("village_code", "string"), ("zone_center", "string"),
    ("cause", "string"), ("title", "string"), ("event_status", "string"),
    ("situation_status", "string"),
    ("relief_declared_date", "date"), ("disaster_area_date", "date"),
    ("other_announce_date", "date"), ("end_disaster_date", "date"),
    ("aid_zone_declaration_date", "date"), ("disaster_declaration_date", "date"),
    ("other_declarations_date", "date"), ("situation_ended_date", "date"),
    ("affected_people", "bigint"), ("affected_households", "bigint"),
    ("evacuated_people", "bigint"), ("evacuated_households", "bigint"),
    ("deaths", "bigint"), ("missing", "bigint"), ("injured", "bigint"),
    ("housing_damage", "double"), ("business_damage", "double"),
    ("agriculture_damage", "double"), ("livestock_damage", "double"),
    ("fishing_damage", "double"), ("transport_damage", "double"),
    ("health_damage", "double"), ("culture_damage", "double"),
    ("education_sports_damage", "double"), ("utilities_damage", "double"),
    ("government_locations_damage", "double"),
    ("other_public_benefits_damage", "double"),
    ("government_property_damage", "double"),
]

# ------------------------------------------------------ fact_disaster_damage
_DAMAGE_COLUMNS = [
    ("source_record_id", "string"), ("district_code", "string"), ("district", "string"),
    ("subdistrict_id", "int"), ("village_id", "int"), ("disaster_date", "date"),
    ("affected_people", "bigint"), ("affected_households", "bigint"),
    ("evacuated_households", "bigint"), ("evacuated_people", "bigint"),
    ("deaths", "bigint"), ("missing_people", "bigint"), ("injured_people", "bigint"),
    ("houses_damaged", "bigint"), ("partially_damaged_houses", "bigint"),
]

# ---------------------------------------------------- fact_household_income
_INCOME_COLUMNS = [
    ("income_record_id", "string"), ("district_code", "string"), ("district", "string"),
    ("subdistrict", "string"), ("area", "string"), ("households", "bigint"),
    ("avg_household_income_baht_per_year", "bigint"),
    ("mapping_match_status", "string"), ("village_code", "string"),
]

TABLES = {
    "dim_village": {
        "source": TRANSFORM_OUT / "village_mapping_transformed.csv",
        "grain": "1 แถว = 1 หมู่บ้านในจังหวัดเชียงใหม่ (ข้อมูล ณ ปีที่สำรวจ ไม่แยกปี)",
        "primary_key": ["village_code"],
        "partition": None,
        "columns": None,  # filled from the CSV header with _village_type()
        "code_lengths": _VILLAGE_CODES,
    },
    "fact_flood_report": {
        "source": TRANSFORM_OUT / "flood_chiangmai_combined.csv",
        "grain": "1 แถว = 1 หมู่บ้านที่ถูกรายงานใน 1 เหตุการณ์อุทกภัย (ปภ.)",
        "primary_key": ["source_year", "source_record_id"],
        "partition": ("source_year", "int"),
        "columns": _FLOOD_COLUMNS,
        "code_lengths": {"province_code": 2, "district_code": 4,
                         "subdistrict_code": 6, "village_code": 8},
    },
    "fact_disaster_damage": {
        "source": TRANSFORM_OUT / "chiangmai_damage_transformed.csv",
        "grain": "1 แถว = 1 รายการความเสียหายจากภัยพิบัติ (อำเภอ/ตำบล/หมู่ ต่อวันที่เกิดเหตุ)",
        "primary_key": ["source_record_id"],
        "partition": ("source_year", "int"),
        "columns": _DAMAGE_COLUMNS,
        "code_lengths": {"district_code": 4},
    },
    "fact_household_income": {
        "source": TRANSFORM_OUT / "household_income_mapping_integrated.csv",
        "grain": "1 แถว = 1 พื้นที่ (บ้าน/ชุมชน) ในข้อมูลรายได้ครัวเรือนเฉลี่ย ไม่มีปีกำกับ",
        "primary_key": ["income_record_id"],
        "partition": None,
        "columns": _INCOME_COLUMNS,
        "code_lengths": {"district_code": 4, "village_code": 8},
    },
}


def village_columns(header):
    return [(c, _village_type(c)) for c in header]
