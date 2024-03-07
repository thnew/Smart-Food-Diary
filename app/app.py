import streamlit as st
import pandas as pd
import json
from classes.meal_input import MealInput
from streamlit_javascript import st_javascript
from io import StringIO

inputs = None

# def get_from_local_storage(k):
#     v = st_javascript(
#         f"JSON.parse(localStorage.getItem('{k}'));"
#     )
#     st.info(f"Resding {v}")

#     return json.loads(v) if v else None

# def set_to_local_storage(k, v):
#     jdata = json.dumps(v)
#     st.info(f"Serializing {jdata}")
#     st_javascript(
#         f"localStorage.setItem('{k}', JSON.stringify({jdata}));"
#     )


# set_to_local_storage("test", '{"name": 123}')
# st.info(get_from_local_storage("test"))

# st.info("DONE")

# input_texts = get_from_local_storage('input_texts')
# parsed_inputs_csv = get_from_local_storage('parsed_inputs')
# if input_texts is not None:
#     #try:
#         st.info(parsed_inputs_csv)
#         parsed_inputs = st.info(pd.read_csv(StringIO(parsed_inputs_csv), delimiter=','))
#         st.info("parsed")
#         inputs = [
#             MealInput('breakfast', 'Breakfast', input_texts[0], parsed_inputs[0]),
#             MealInput('lunch', 'Lunch', input_texts[1], parsed_inputs[1]),
#             MealInput('dinner', 'Dinner', input_texts[2], parsed_inputs[2])
#         ]
#     #except:
#     #    st.error("Sth went wrong")
#     #    inputs = None

if inputs == None:
    inputs = [
        MealInput('breakfast', 'Breakfast'),
        MealInput('lunch', 'Lunch'),
        MealInput('dinner', 'Dinner'),
    ]

st.title("Food Diary")
st.markdown("Start filling out your diary to see your calories")

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
    input.input_text = st.text_area(input.title, placeholder="1 egg and a glass of milk")
    input.parsed_meals = extract_meals_from_input(input.input_text)

    st.dataframe(input.parsed_meals)

# set_to_local_storage("input_texts", {'list': [input.input_text for input in inputs]})
# set_to_local_storage("parsed_inputs", {'list': [input.parsed_meals.to_csv() for input in inputs]})

[input.parsed_meals.to_csv() for input in inputs]
