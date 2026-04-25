import pandas as pd

# Load original dataset
df = pd.read_csv("/Users/annazakreva/Documents/GitHub/HackUPC2026/rules data/antipatterns.csv")  # replace with your file name

# Build "bad" rows
bad_df = df[["name", "category", "bad_example"]].copy()
bad_df["type"] = "wrong"
bad_df = bad_df.rename(columns={"bad_example": "code"})

# Build "good" rows
good_df = df[["name", "category", "good_example"]].copy()
good_df["type"] = "good"
good_df = good_df.rename(columns={"good_example": "code"})

# Combine both
test_examples = pd.concat([bad_df, good_df], ignore_index=True)

# Reorder columns
test_examples = test_examples[["code", "type", "name", "category"]]

# Save to CSV
test_examples.to_csv("/Users/annazakreva/Documents/GitHub/HackUPC2026/code tests/AntiPatternsDataset/test_examples.csv", index=False)

print("test_examples.csv created successfully")