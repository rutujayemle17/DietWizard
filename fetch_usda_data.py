import requests
import pandas as pd
import time
import os

# USDA API Key (Replace with your actual key)
API_KEY = "NkM4bvKeRteumDIuugBADuyWCQ3icYsdeajEKQdS"

# List of food items to fetch
food_items = ["oatmeal", "eggs", "toast", "pancake", "cereal", "chicken", "rice", "dal", "roti", "salad"]
csv_file = "food_data.csv"

# Function to fetch food data from the USDA API
def fetch_food_data(food_name):
    try:
        url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_name}&api_key={API_KEY}"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code} for {food_name}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

# Check if the CSV file exists
if os.path.exists(csv_file):
    existing_data = pd.read_csv(csv_file)
else:
    existing_data = pd.DataFrame(columns=["Food Name", "Calories", "Protein", "Carbs", "Fats"])

# Fetch and store data
new_data = []

for food in food_items:
    print(f"Fetching data for: {food}")
    data = fetch_food_data(food)

    if data and "foods" in data:
        for item in data["foods"][:5]:  # Get first 5 results
            name = item.get("description", "Unknown")
            calories = next((n["value"] for n in item.get("foodNutrients", []) if n.get("nutrientName") == "Energy"), "N/A")
            protein = next((n["value"] for n in item.get("foodNutrients", []) if n.get("nutrientName") == "Protein"), "N/A")
            carbs = next((n["value"] for n in item.get("foodNutrients", []) if n.get("nutrientName") == "Carbohydrate, by difference"), "N/A")
            fats = next((n["value"] for n in item.get("foodNutrients", []) if n.get("nutrientName") == "Total lipid (fat)"), "N/A")

            # Avoid duplicates
            if not ((existing_data["Food Name"] == name) & (existing_data["Calories"] == calories)).any():
                new_data.append([name, calories, protein, carbs, fats])

        time.sleep(1)  # Delay to prevent too many API requests
    else:
        print(f"No data found for {food}")

# Save to CSV
if new_data:
    new_df = pd.DataFrame(new_data, columns=["Food Name", "Calories", "Protein", "Carbs", "Fats"])
    updated_df = pd.concat([existing_data, new_df], ignore_index=True)
    updated_df.to_csv(csv_file, index=False)
    print("✅ New food data has been added to CSV!")
else:
    print("⚠️ No new data added.")
