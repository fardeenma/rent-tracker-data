import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date
import os
import re
import json

print("Script started...")

URL = "https://www.highlandsatsugarloaf.com/floorplans"

EXTRA_COSTS = 344

FLOORPLANS = {
    "The Centennial": {"sqft": 831},
    "The Grant": {"sqft": 1088},
}

response = requests.get(URL, timeout=20)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
text = soup.get_text(" ", strip=True)

today = str(date.today())
rows = []

for floorplan, info in FLOORPLANS.items():

    pattern = rf"{floorplan}.*?Starting at \$([\d,]+\.\d{{2}})"
    match = re.search(pattern, text)

    if not match:
        print(f"Could not find price for {floorplan}")
        continue

    base_rent = float(match.group(1).replace(",", ""))

    estimated_total = base_rent + EXTRA_COSTS

    rows.append({
        "Date": today,
        "Floorplan": floorplan,
        "Sq Ft": info["sqft"],
        "Base Rent": base_rent,
        "Estimated Total": estimated_total
    })

if not rows:
    raise Exception("No floorplan prices found.")

new_df = pd.DataFrame(rows)

    final_df = new_df

# -------- JSON DATA FOR ESP32 --------

floorplan_data = []

for floorplan in ["The Grant", "The Centennial"]:

    plan_rows = final_df[final_df["Floorplan"] == floorplan]

    current_rent = int(plan_rows.iloc[-1]["Base Rent"])
    low_rent = int(plan_rows["Base Rent"].min())
    high_rent = int(plan_rows["Base Rent"].max())

    floorplan_data.append({
        "name": floorplan,
        "current": current_rent,
        "low": low_rent,
        "high": high_rent
    })

rent_data = {
    "floorplans": floorplan_data
}

with open("rent_data.json", "w") as f:
    json.dump(rent_data, f, indent=4)
print("Rent tracker updated!")
print(new_df)

print("Script completed successfully.")