import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from components.highlighted_textarea import highlighted_textarea
from classes.meal_input import MealInput
from annotated_text import annotated_text

load_dotenv()
api_url = os.environ.get('API_URL')

st.markdown("""
    <h1>What did you eat today?</h1>
    <div class="subtitle">Start typing to see your calories</div>
    <style>
        .block-container {
            padding-left: 0 !important;
            padding-right: 0 !important;
        }
        h1 {
            text-align: center;
        }
        h1 span {
            font-size: 48px;
            color: #20405F;
        }

        .subtitle {
            color: #64748B;
            text-align: center;
            font-size: 1.25rem;
            font-style: normal;
            font-weight: 400;
            line-height: 150%;
        }
    </style>
    """, unsafe_allow_html=True)

input = MealInput('breakfast', 'Breakfast').load_from_cache()

result = highlighted_textarea(
    initial_value=input.value,
    api_url=api_url,
    key=input.id)

# We cache texts and results for next reload
input.value = result['value']
input.store_in_cache()

input.extracted_meals = result['dataframe']

if input.extracted_meals is not None and 'matched_calories' in input.extracted_meals.columns:
    total = input.extracted_meals['matched_calories'].sum()
    st.write(f"Total: {total}ccal")

st.stop()
st.write(", ".join([f"{cal}ccal" for cal in input.extracted_meals['matched_calories']]))

if input.extracted_meals.shape[0] > 0:
    st.subheader("Found datasets")
    st.dataframe(input.extracted_meals)
