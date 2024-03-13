import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from components.highlighted_textarea import highlighted_textarea
from classes.extract_meals_from_text import extract_meals_from_input
from classes.meal_input import MealInput
from annotated_text import annotated_text

load_dotenv()
api_url = os.environ.get('API_URL')

title_cell_1, title_cell_2 = st.columns([3, 1])
# title_cell_1.markdown("""
#     <h1>Food Diary</h1>
#     <style>
#         h1 span {
#             font-size: 72px;
#             background: -webkit-linear-gradient(45deg, #9883E5, #72A1E5 80%);
#             -webkit-background-clip: text;
#             -webkit-text-fill-color: transparent;
#         }
#     </style>
#     """, unsafe_allow_html=True)
title_cell_1.title("Food Diary")
st.markdown("Start filling out your diary to see your calories")

# title_cell_2.text('')
title_cell_2.text('')
title_cell_2.text('')
#config_popover = title_cell_2.popover("Config")
show_details = st.toggle('Show detailed output', True)

inputs = [
    MealInput('breakfast', 'Breakfast').load_from_cache(),
    MealInput('lunch', 'Lunch').load_from_cache(),
    MealInput('dinner', 'Dinner').load_from_cache()
]

for input in inputs:
    with st.container(border=True):
        st.subheader(input.title)

        result = highlighted_textarea(
            initial_value=input.value,
            api_url=api_url,
            key=input.id)

        # We cache texts and results for next reload
        input.value = result['value']
        input.store_in_cache()

        input.extracted_meals = result['dataframe']

        st.write(", ".join([f"{cal}ccal" for cal in input.extracted_meals['matched_calories']]))

        if input.extracted_meals.shape[0] > 0:
            #annotated = get_annotated_input_text(input.input_text, input.extracted_meals)

            if show_details:
                st.subheader("Found datasets")
                st.dataframe(input.extracted_meals)

st.subheader("Total")
all_nutrition_values = pd.concat([x.extracted_meals for x in inputs])
all_nutrition_values['name'] = all_nutrition_values['matched_name']# + ", " + all_nutrition_values['matched_quantity'].str + " " + all_nutrition_values['matched_unit']
all_nutrition_values = all_nutrition_values[['name', 'matched_calories', 'matched_carbs', 'matched_protein', 'matched_fat']]
all_nutrition_values = pd.concat([
    all_nutrition_values,
    pd.DataFrame({
        'name': ["Total"],
        'matched_calories': [sum(all_nutrition_values['matched_calories'].astype(int))],
        'matched_carbs': [sum(all_nutrition_values['matched_carbs'].astype(int))],
        'matched_protein': [sum(all_nutrition_values['matched_protein'].astype(int))],
        'matched_fat': [sum(all_nutrition_values['matched_fat'].astype(int))]
    })
])
st.dataframe(all_nutrition_values)
