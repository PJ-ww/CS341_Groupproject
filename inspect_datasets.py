
import pandas as pd
from pathlib import Path

DATA_DIR = Path("validation/cleaned")

FILES = [
    "flood_2566_cleaned.csv",
    "flood_2567_cleaned.csv",
    "chiangmai_damage_cleaned.csv",
    "household_income_cleaned.csv",
    "village_mapping_cleaned.csv",
]

for filename in FILES:
    file_path = DATA_DIR / filename

    print("\n" + "=" * 80)
    print(f"FILE: {filename}")

    df = pd.read_csv(file_path, dtype=str, low_memory=False)

    print("SHAPE:", df.shape)

    print("\nCOLUMNS:")
    for column in df.columns:
        print(f"- {column}")

    print("\nMISSING VALUES:")
    print(df.isna().sum().to_string())

    print("\nSAMPLE DATA:")
    print(df.head(3).to_string(index=False))

print("\nFinished inspecting all datasets.")
