import streamlit as st
import pandas as pd
from classes.meal_input import MealInput

st.title("Food Diary")
st.markdown("Start filling out your diary to see your calories")

inputs = [
    MealInput('breakfast', 'Breakfast').load_from_local_storage(),
    MealInput('lunch', 'Lunch').load_from_local_storage(),
    MealInput('dinner', 'Dinner').load_from_local_storage(),
]

# Split up input in rows and extract
def extract_meals_from_input(text: str) -> pd.DataFrame:
    rows = text.split("\n")

    # Go through every row and parse the meal names, units and amounts of of them
    meals = pd.DataFrame(columns=['meal_name', 'amount', 'unit'])
    for row in rows:
        meals = pd.concat([meals, extract_meals_from_text(row)])

    return meals.reset_index(drop=True)

def extract_meals_from_text(text: str) -> pd.DataFrame:
    if len(text) == 0:
        return pd.DataFrame(columns=['meal_name', 'amount', 'unit'])

    # TODO: Replace with AI

    return pd.DataFrame({
        'meal_name': [text, 'milk'],
        'amount': ['1', '1'],
        'unit': ['piece', 'glass'],
    })

for input in inputs:
    input.input_text = st.text_area(
        input.title,
        value=input.input_text,
        placeholder="1 egg and a glass of milk")
    input.parsed_meals = extract_meals_from_input(input.input_text)

    st.dataframe(input.parsed_meals)

for input in inputs:
    input.store_in_local_storage()
