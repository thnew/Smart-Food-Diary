import pandas as pd
import difflib
from difflib import SequenceMatcher

nutrition_dataset = pd.read_csv('data/nutrition_dataset.csv', delimiter=',')

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

def get_annotated_input_text(input_text: str, parsed_meals: pd.DataFrame) -> list:
    annotated_parts = []

    last_end = 0
    for _, row in parsed_meals.iterrows():
        start_index = min_pos(row['food_start'], row['quantity_start'], row['unit_start'])
        end_index = max_pos(row['food_end'], row['quantity_end'], row['unit_end'])

        # Add text that has not been recognized as food, quantity or unit
        if last_end < start_index:
            annotated_parts.append(f" {input_text[last_end:start_index]} ")

        calories = row['matched_calories']
        annotated_parts.append((input_text[start_index:end_index].strip(), f"{calories}ccal"))

        last_end = end_index

    return annotated_parts

def min_pos(*args):
    return min([x for x in args if x != -1])

def max_pos(*args):
    return max([x for x in args if x != -1])

if __name__ == "__main__":
    print(get_nutrition_values(pd.DataFrame({
        'food': ['bla', 'milk'],
        'quantity': ['1', '1'],
        'unit': ['piece', 'glass'],
    })))
