import pandas as pd
from pathlib import Path

DATA = Path("validation/cleaned")

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

mapping["mcode"] = mapping["mcode"].str.strip()

for year, df in [("2566", f66), ("2567", f67)]:
    cm = df[
        df["Province Code"].fillna("").str.strip() == "50"
    ].copy()

    cm["Village Code"] = (
        cm["Village Code"].fillna("").str.strip()
    )

    print(f"\n===== MAPPING COVERAGE {year} =====")

    flood_districts = set(
        cm["District"].dropna().str.strip()
    )

    mapping_districts = set(
        mapping["aname"].dropna().str.strip()
    )

    print("Flood districts:", len(flood_districts))
    print("Mapping districts:", len(mapping_districts))
    print("Districts not found in mapping:")

    for district in sorted(flood_districts - mapping_districts):
        print("-", district)

    matched_codes = set(cm["Village Code"]) & set(mapping["mcode"])

    print("\nMatched village codes:", len(matched_codes))
    print("Total unique flood village codes:", cm["Village Code"].nunique())
