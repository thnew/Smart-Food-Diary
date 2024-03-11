import pandas as pd
import difflib
from difflib import SequenceMatcher

# TODO: Replace with real dataset
nutrition_dataset = pd.read_csv('data/test_nutrition_dataset.csv', delimiter=';')

food_names = nutrition_dataset['Meal'].dropna().tolist()

def closest_matches(meal_name: str):
    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()

    matches = difflib.get_close_matches(meal_name, food_names)

    if len(matches) == 0:
        return None

    return [{ 'title': x, 'similarity': similar(x, meal_name) } for x in matches]

def get_nutrition_values(meals: pd.DataFrame) -> list:
    match_columns = ['matched_food', 'matched_quantity', 'matched_unit', 'matched_calories', 'matched_carbs', 'matched_protein', 'matched_fat']
    meals[match_columns] = None

    for index, row in meals.iterrows():
        matches = closest_matches(row['food'])

        if matches is None:
            continue

        # Find match in nutrition dataset
        best_match = matches[0]
        matched_nutrition_dataset = nutrition_dataset[nutrition_dataset['Meal'] == best_match['title']]
        df_best_match = matched_nutrition_dataset.iloc[0]
        df_best_match = df_best_match[['Meal', 'Amount', 'Units', 'Calories', 'Carbs', 'Protein', 'Fat']]
        df_best_match.index = match_columns

        meals.loc[index, match_columns] = df_best_match

    return meals

if __name__ == "__main__":
    print(get_nutrition_values(pd.DataFrame({
        'food': ['bla', 'milk'],
        'quantity': ['1', '1'],
        'unit': ['piece', 'glass'],
    })))
