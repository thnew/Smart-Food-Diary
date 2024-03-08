import streamlit as st
import pandas as pd
from classes.get_nutrition_values import get_nutrition_values
from classes.extract_meals_from_text import extract_meals_from_input
from classes.meal_input import MealInput

st.title("Food Diary")
st.markdown("Start filling out your diary to see your calories")

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
    input.parsed_meals = extract_meals_from_input(input.input_text)

    nutrition_values = get_nutrition_values(input.parsed_meals)

    st.dataframe(nutrition_values)

for input in inputs:
    input.store_in_local_storage()
