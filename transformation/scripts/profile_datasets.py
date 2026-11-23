import pandas as pd
from pathlib import Path

DATA = Path("validation/cleaned")


def compare_village_codes(flood_df, mapping_codes, year):
    codes = flood_df["Village Code"].fillna("").str.strip()

    flood_codes = set(codes[codes != ""])

    matched = flood_codes & mapping_codes
    unmatched = flood_codes - mapping_codes

    print(f"\n=== VILLAGE CODE MATCHING: {year} ===")
    print("Flood rows:", len(flood_df))
    print("Unique flood codes:", len(flood_codes))
    print("Missing Village Code rows:", (codes == "").sum())
    print("Matched codes:", len(matched))
    print("Unmatched codes:", len(unmatched))

    if unmatched:
        print("\nUnmatched Village Codes:")
        for code in sorted(unmatched):
            print(code)


# Load Flood 2566
f66 = pd.read_csv(
    DATA / "flood_2566_cleaned.csv",
    dtype=str
)

f66_cm = f66[
    f66["Province Code"].fillna("").str.strip() == "50"
]

print("\n=== FLOOD 2566: CHIANG MAI ===")
print("Rows:", len(f66_cm))
print("Districts:", f66_cm["District"].nunique())
print(f66_cm["District"].value_counts().to_string())


# Load Flood 2567
f67 = pd.read_csv(
    DATA / "flood_2567_cleaned.csv",
    dtype=str
)

f67_cm = f67[
    f67["Province Code"].fillna("").str.strip() == "50"
]

print("\n=== FLOOD 2567: CHIANG MAI ===")
print("Rows:", len(f67_cm))
print("Districts:", f67_cm["District"].nunique())
print(f67_cm["District"].value_counts().to_string())


# Chiang Mai Damage
damage = pd.read_csv(
    DATA / "chiangmai_damage_cleaned.csv",
    dtype=str
)

print("\n=== CHIANG MAI DAMAGE ===")
print("Rows by year:")
print(
    damage["ปี"].value_counts(dropna=False)
    .sort_index()
    .to_string()
)


# Village Mapping
village = pd.read_csv(
    DATA / "village_mapping_cleaned.csv",
    dtype=str
)

print("\n=== VILLAGE MAPPING ===")
print("Rows:", len(village))
print("Unique mcode:", village["mcode"].nunique())
print("Duplicate mcode:", village["mcode"].duplicated().sum())

mapping_codes = set(
    village["mcode"].dropna().str.strip()
)


# Compare both years
compare_village_codes(f66_cm, mapping_codes, "2566")
compare_village_codes(f67_cm, mapping_codes, "2567")
