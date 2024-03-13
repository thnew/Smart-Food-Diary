import streamlit as st
import pandas as pd
import difflib
from difflib import SequenceMatcher
import time

# TODO: This will load the dataframe on every request, we should cache it or move it to the API
nutrition_dataset = pd.read_csv('../data/nutrition_dataset.csv', delimiter=',')
print("LOAD")
# nutrition_dataset = nutrition_dataset.sample(10000)

food_names = nutrition_dataset['Meal'].dropna().tolist()

#@st.cache_data
def closest_matches(meal_name: str):
    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()

    matches = difflib.get_close_matches(meal_name, food_names)

    if len(matches) == 0:
        return None

    return [{ 'title': x, 'similarity': similar(x, meal_name) } for x in matches]

def get_nutrition_values(meals: pd.DataFrame) -> pd.DataFrame:
    match_columns = ['matched_food', 'matched_quantity', 'matched_unit', 'matched_calories', 'matched_carbs', 'matched_protein', 'matched_fat']
    meals[match_columns] = None
    time = current_milli_time()

    for index, row in meals.iterrows():
        matches = closest_matches(row['food'])

        if matches is None:
            continue

        # Find match in nutrition dataset
        best_match = matches[0]
        df_best_match = get_dataset_for_meal(best_match['title'], match_columns)

        meals.loc[index, match_columns] = df_best_match

    print("TIME TO FIND ALL IN DATASET", current_milli_time() - time)

    float_columns = [
        'food_start',
        'food_end',
        'unit_start',
        'unit_end',
        'quantity_start',
        'quantity_end',
        'matched_quantity',
        'matched_calories',
        'matched_carbs',
        'matched_protein',
        'matched_fat']
    meals[float_columns] = meals[float_columns].astype(float)

    return meals

#@st.cache_data
def get_dataset_for_meal(meal_name: str, match_columns: pd.DataFrame) -> pd.DataFrame:
    matched_nutrition_dataset = nutrition_dataset[nutrition_dataset['Meal'] == meal_name]

    df_best_match = matched_nutrition_dataset.iloc[0]
    df_best_match = df_best_match[['Meal', 'Amount', 'Units', 'Calories', 'Carbs', 'Protein', 'Fat']]
    df_best_match.index = match_columns

    return df_best_match

# Colors from here: https://coolors.co/visualizer/2e382e-50c9ce-72a1e5-9883e5-fcd3de
colors = [
    '#50C9CE',
    '#72A1E5',
    '#9883E5',
    '#FCD3DE'
]

def get_text_highlight_colors(input_text: str, parsed_meals: pd.DataFrame) -> list:
    annotated_parts = []

    for index, row in parsed_meals.iterrows():
        start_index = min_pos(row['food_start'], row['quantity_start'], row['unit_start'])
        end_index = max_pos(row['food_end'], row['quantity_end'], row['unit_end'])

        annotated_parts.append((start_index, end_index, colors[index % len(colors)]))

    return annotated_parts

def get_annotated_input_text(input_text: str, parsed_meals: pd.DataFrame) -> list:
    annotated_parts = []

    last_end = 0
    for index, row in parsed_meals.iterrows():
        start_index = min_pos(row['food_start'], row['quantity_start'], row['unit_start'])
        end_index = max_pos(row['food_end'], row['quantity_end'], row['unit_end'])

        # Add text that has not been recognized as food, quantity or unit
        if last_end < start_index:
            annotated_parts.append(f" {input_text[last_end:start_index]} ")

        calories = row['matched_calories']
        annotated_parts.append((input_text[start_index:end_index].strip(), f"{calories}ccal", colors[index % len(colors)]))

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


def current_milli_time():
    return round(time.time() * 1000)
