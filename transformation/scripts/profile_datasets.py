import pandas as pd
from pathlib import Path

DATA = Path("validation/cleaned")

# Flood 2566
f66 = pd.read_csv(DATA / "flood_2566_cleaned.csv", dtype=str)
f66_cm = f66[f66["Province Code"].str.strip() == "50"]

print("\n=== FLOOD 2566: CHIANG MAI ===")
print("Rows:", len(f66_cm))
print("Districts:", f66_cm["District"].nunique())
print(f66_cm["District"].value_counts().to_string())

# Flood 2567
f67 = pd.read_csv(DATA / "flood_2567_cleaned.csv", dtype=str)
f67_cm = f67[f67["Province Code"].str.strip() == "50"]

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
print(damage["ปี"].value_counts(dropna=False).sort_index().to_string())

# Village Mapping
village = pd.read_csv(
    DATA / "village_mapping_cleaned.csv",
    dtype=str
)

print("\n=== VILLAGE MAPPING ===")
print("Rows:", len(village))
print("Unique mcode:", village["mcode"].nunique())
print("Duplicate mcode:", village["mcode"].duplicated().sum())

# Compare village codes
flood_codes = set(f66_cm["Village Code"].dropna().str.strip())
mapping_codes = set(village["mcode"].dropna().str.strip())

print("\n=== VILLAGE CODE MATCHING ===")
print("Flood 2566 codes:", len(flood_codes))
print("Mapping codes:", len(mapping_codes))
print("Matched:", len(flood_codes & mapping_codes))
print("Unmatched:", len(flood_codes - mapping_codes))
