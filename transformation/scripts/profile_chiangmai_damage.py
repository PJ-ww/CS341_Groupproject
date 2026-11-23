import pandas as pd
from pathlib import Path

DATA = Path("validation/cleaned")

df = pd.read_csv(
    DATA / "chiangmai_damage_cleaned.csv",
    dtype=str
)

# Filter only years 2566 and 2567
df = df[df["ปี"].str.strip().isin(["2566", "2567"])].copy()

print("\n===== CHIANG MAI DAMAGE PROFILE =====")
print("Rows:", len(df))

print("\nRows by year:")
print(df["ปี"].value_counts().sort_index().to_string())

print("\nRows by district:")
print(
    df.groupby(["ปี", "อำเภอ"]).size()
    .to_string()
)

print("\nUnique values:")
for col in ["อำเภอ", "ตำบล", "หมู่บ้าน"]:
    print(f"{col}: {df[col].nunique()}")

print("\nSample village values:")
print(
    df[["ปี", "อำเภอ", "ตำบล", "หมู่บ้าน"]]
    .drop_duplicates()
    .head(30)
    .to_string(index=False)
)

print("\nDuplicate combinations:")
keys = ["ปี", "อำเภอ", "ตำบล", "หมู่บ้าน"]

print("Duplicate rows:", df.duplicated(subset=keys).sum())

print("\nMissing values:")
print(df.isna().sum().to_string())


print("\n===== DUPLICATE ANALYSIS =====")

keys_without_date = [
    "ปี", "อำเภอ", "ตำบล", "หมู่บ้าน"
]

keys_with_date = [
    "ปี", "อำเภอ", "ตำบล", "หมู่บ้าน", "วันที่เกิดภัย"
]

print(
    "Duplicates without date:",
    df.duplicated(subset=keys_without_date).sum()
)

print(
    "Duplicates with date:",
    df.duplicated(subset=keys_with_date).sum()
)

# Show records that repeat by year, district, subdistrict and village
duplicate_records = df[
    df.duplicated(
        subset=keys_without_date,
        keep=False
    )
].sort_values(keys_without_date + ["วันที่เกิดภัย"])

print("\nRepeated village records:")
print(
    duplicate_records[
        keys_with_date + [
            "ราษฎร(คน)",
            "ราษฎร(ครัวเรือน)",
            "เสียชีวิต(คน)",
            "บ้านพักอาศัย(หลัง)"
        ]
    ].to_string(index=False)
)

print("\nUnique disaster dates by year:")
print(
    df.groupby("ปี")["วันที่เกิดภัย"]
    .nunique()
    .to_string()
)


print("\n===== NUMERIC DATA QUALITY CHECK =====")

numeric_columns = [
    "ราษฎร(คน)",
    "ราษฎร(ครัวเรือน)",
    "อพยพ(ครัวเรือน)",
    "อพยพ(คน)",
    "เสียชีวิต(คน)",
    "สูญหาย(คน)",
    "บาดเจ็บ(คน)",
    "บ้านพักอาศัย(หลัง)"
]

for col in numeric_columns:
    values = pd.to_numeric(df[col], errors="coerce")

    print(f"\nColumn: {col}")
    print("Invalid numeric values:", values.isna().sum())
    print("Minimum:", values.min())
    print("Maximum:", values.max())

    print("\nTop 5 largest records:")

    top = df.loc[
        values.nlargest(5).index,
        ["ปี", "อำเภอ", "ตำบล", "หมู่บ้าน", "วันที่เกิดภัย", col]
    ]

    print(top.to_string(index=False))


