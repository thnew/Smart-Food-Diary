import streamlit as st
from classes.get_nutrition_values import get_nutrition_values
from classes.extract_meals_from_text import extract_meals_from_input
from classes.meal_input import MealInput
from annotated_text import annotated_text
import pandas as pd

st.title("Food Diary")
st.markdown("Start filling out your diary to see your calories")

def get_annotated_input_text(input_text: str, parsed_meals: pd.DataFrame) -> list:
    annotated_parts = []

    last_end = 0
    for _, row in parsed_meals.iterrows():
        start_index = min_pos(row['food_start'], row['quantity_start'], row['unit_start'])
        end_index = max_pos(row['food_end'], row['quantity_end'], row['unit_end'])

        # Add text that has not been recognized as food, quantity or unit
        if last_end < start_index:
            annotated_parts.append(f" {input_text[last_end:start_index]} ")
            last_end = end_index

        calories = row['matched_calories']
        annotated_parts.append((input_text[start_index:end_index].strip(), f"{calories}ccal"))

    return annotated_parts

def min_pos(*args):
    return min([x for x in args if x != -1])

def max_pos(*args):
    return max([x for x in args if x != -1])

with st.expander("Config"):
    use_chat_gpt = st.toggle('Use ChatGPT for meal extraction')
    show_details = st.toggle('Show detailed output', True)

    inputs = [
        MealInput('breakfast', 'Breakfast').load_from_local_storage(),
        MealInput('lunch', 'Lunch').load_from_local_storage(),
        MealInput('dinner', 'Dinner').load_from_local_storage(),
    ]

for input in inputs:
    input.input_text = st.text_area(
        input.title,
        value=input.input_text,
        placeholder="1 egg and a glass of milk")

    input.parsed_meals = extract_meals_from_input(input.input_text, use_chat_gpt)

    if show_details:
        st.subheader("Extracted meals")
        st.dataframe(input.parsed_meals)

    nutrition_values = get_nutrition_values(input.parsed_meals)

    if input.parsed_meals.shape[0] > 0:
        annotated = get_annotated_input_text(input.input_text, input.parsed_meals)
        annotated_text(*annotated)

        if show_details:
            st.subheader("Found datasets")
            st.dataframe(nutrition_values)

# We cache texts and results for next reload
for input in inputs:
    input.store_in_local_storage()
