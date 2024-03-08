import pandas as pd
import difflib
from difflib import SequenceMatcher

# TODO: Replace with real dataset
nutrition_dataset = pd.read_csv('data/test_nutrition_dataset.csv')

food_names = nutrition_dataset['Meal'].dropna().tolist()

def closest_matches(meal_name: str):
    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()

    matches = difflib.get_close_matches(meal_name, food_names)

    if len(matches) == 0:
        return None

    return [{ 'title': x, 'similarity': similar(x, meal_name) } for x in matches]

def get_nutrition_values(extracted_meals: pd.DataFrame) -> list:
    found_food = []
    for i in range(len(extracted_meals)):
        row = extracted_meals.iloc[i]

        matches = closest_matches(row['Meal'])

        if matches is None:
            continue

        # Find match in nutrition dataset
        match = matches[0]
        matched_nutrition_dataset = nutrition_dataset[nutrition_dataset['Meal'] == match['title']]

        found_food.append(matched_nutrition_dataset.iloc[0])

    return found_food

if __name__ == "__main__":
    print(get_nutrition_values(pd.DataFrame({
        'Meal': ['bla', 'milk'],
        'Amount': ['1', '1'],
        'Unit': ['piece', 'glass'],
    })))
