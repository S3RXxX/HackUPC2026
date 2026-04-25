import pandas as pd

# Load original dataset
df = pd.read_csv("/Users/annazakreva/Documents/GitHub/HackUPC2026/rules data/bad-project.csv")  # replace with your file name

# Build "bad" rows
bad_df = df[["Name", "Message", "Wrong Example"]].copy()
bad_df["type"] = "wrong"
bad_df = bad_df.rename(columns={"Wrong Example": "code"})

# Build "good" rows
good_df = df[["Name", "Message", "Good Example"]].copy()
good_df["type"] = "good"
good_df = good_df.rename(columns={"Good Example": "code"})

# Combine both
test_examples = pd.concat([bad_df, good_df], ignore_index=True)

# Reorder columns
test_examples = test_examples[["code", "type", "Name", "Message"]]

# Save to CSV
test_examples.to_csv("/Users/annazakreva/Documents/GitHub/HackUPC2026/code tests/BadProjectDataset/test_examples.csv", index=False)

print("test_examples.csv created successfully")