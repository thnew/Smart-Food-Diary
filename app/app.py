import streamlit as st
from classes.get_nutrition_values import get_annotated_input_text, get_nutrition_values
from classes.extract_meals_from_text import extract_meals_from_input
from classes.meal_input import MealInput
from annotated_text import annotated_text

title_cell_1, title_cell_2 = st.columns([3, 1])
title_cell_1.title("Food Diary")
st.markdown("Start filling out your diary to see your calories")

title_cell_2.text('')
config_popover = title_cell_2.popover("Config")
use_chat_gpt = config_popover.toggle('Use ChatGPT for meal extraction')
show_details = config_popover.toggle('Show detailed output')

inputs = [
    MealInput('breakfast', 'Breakfast').load_from_cache(),
    MealInput('lunch', 'Lunch').load_from_cache(),
    MealInput('dinner', 'Dinner').load_from_cache()
]

for input in inputs:
    with st.container(border=True):
        st.subheader(input.title)

        input.input_text = st.text_area(
            input.id,
            label_visibility='collapsed',
            value=input.input_text,
            placeholder="1 egg and a glass of milk")

        input.parsed_meals = extract_meals_from_input(input.input_text, use_chat_gpt)

        nutrition_values = get_nutrition_values(input.parsed_meals)

        if input.parsed_meals.shape[0] > 0:
            annotated = get_annotated_input_text(input.input_text, input.parsed_meals)
            annotated_text(*annotated)

            if show_details:
                st.subheader("Found datasets")
                st.dataframe(nutrition_values)

# We cache texts and results for next reload
for input in inputs:
    input.store_in_cache()
