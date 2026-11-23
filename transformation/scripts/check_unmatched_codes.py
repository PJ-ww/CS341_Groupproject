import pandas as pd
from pathlib import Path

DATA = Path("validation/cleaned")

# Unmatched codes from profiling
unmatched_codes = {
    "50150702", "50150703", "50170610", "50220102",
    "50060403", "50060503", "50100114", "50100217",
    "50100610", "50121011", "50150701", "50151008",
    "50220308"
}

mapping = pd.read_csv(
    DATA / "village_mapping_cleaned.csv",
    dtype=str
)

f66 = pd.read_csv(
    DATA / "flood_2566_cleaned.csv",
    dtype=str
)

f67 = pd.read_csv(
    DATA / "flood_2567_cleaned.csv",
    dtype=str
)

for year, df in [("2566", f66), ("2567", f67)]:
    cm = df[
        df["Province Code"].fillna("").str.strip() == "50"
    ].copy()

    cm["Village Code"] = (
        cm["Village Code"].fillna("").str.strip()
    )

    result = cm[
        cm["Village Code"].isin(unmatched_codes)
    ]

    print(f"\n===== UNMATCHED DETAILS: {year} =====")

    columns = [
        "Village Code",
        "District",
        "Subdistrict",
        "Moo",
        "Village Code"
    ]

    columns = list(dict.fromkeys(
        col for col in columns if col in result.columns
    ))

    print(
        result[columns]
        .drop_duplicates()
        .sort_values("Village Code")
        .to_string(index=False)
    )

print("\n===== CHECK MAPPING CODES =====")

mapping["mcode"] = mapping["mcode"].fillna("").str.strip()

print(
    mapping[
        mapping["mcode"].isin(unmatched_codes)
    ][["mcode", "aname", "tname", "mname"]]
    .to_string(index=False)
)
