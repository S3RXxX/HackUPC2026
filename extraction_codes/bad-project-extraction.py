import os
import csv

ROOT = "python-bad-project"

def categorize(path):
    parts = path.lower()
    if "bug" in parts:
        return "bug"
    if "vulnerability" in parts:
        return "vulnerability"
    if "duplication" in parts:
        return "duplication"
    if "complex" in parts:
        return "complex_code"
    return "code_smell"


def analyze_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    issues = []

    if "=[]" in code or "={}" in code:
        issues.append("mutable_default_argument")

    if "execute(" in code and "%" in code:
        issues.append("sql_injection")

    if code.count("if") > 10:
        issues.append("high_branching")

    if "password =" in code:
        issues.append("hardcoded_credentials")

    return issues


rows = []

for root, _, files in os.walk(ROOT):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            category = categorize(path)
            issues = analyze_file(path)

            for issue in issues:
                rows.append({
                    "file": path,
                    "category": category,
                    "issue": issue
                })


with open("analysis.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["file", "category", "issue"])
    writer.writeheader()
    writer.writerows(rows)