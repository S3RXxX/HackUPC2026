import requests
from bs4 import BeautifulSoup
import csv

URL = "https://docs.astral.sh/ruff/rules/"

def fetch_tables():
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    rows = []

    # Find all tables
    tables = soup.find_all("table")

    for table in tables:
        headers = [th.get_text(strip=True) for th in table.find_all("th")]

        # Only keep tables with desired columns
        if headers[:3] != ["Code", "Name", "Message"]:
            continue

        for tr in table.find_all("tr")[1:]:  # skip header row
            cols = tr.find_all("td")
            if len(cols) < 3:
                continue

            code = cols[0].get_text(strip=True)
            name = cols[1].get_text(strip=True)
            message = cols[2].get_text(strip=True)

            rows.append({
                "Code": code,
                "Name": name,
                "Message": message
            })

    return rows


def save_to_csv(rows, filename="ruff_rules.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Code", "Name", "Message"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    data = fetch_tables()
    save_to_csv(data)
    print(f"Saved {len(data)} rows to ruff_rules.csv")