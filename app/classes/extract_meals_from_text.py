import streamlit as st
import pandas as pd
import json
import os
from transformers import pipeline
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
apikey = os.environ.get('OPENAPI_APIKEY')

# Split up input in rows and extract
def extract_meals_from_input(text: str, use_chat_gpt: bool) -> pd.DataFrame:
    # We process inputs row by row
    rows = text.split("\n")

    # Go through every row and parse the meal names, units and amounts of of them
    meals = pd.DataFrame(columns=['Meal', 'Amount', 'Unit'])
    for row in rows:
        meals = pd.concat([meals, extract_meals_from_text(row, use_chat_gpt)])

    return meals.reset_index(drop=True)

def extract_meals_from_text(food_diary_entry: str, use_chat_gpt: bool) -> pd.DataFrame:
    if len(food_diary_entry) == 0:
        return pd.DataFrame(columns=['Meal', 'Amount', 'Unit'])

    if use_chat_gpt:
        return get_result_from_chat_gpt3(food_diary_entry)

    return get_result_from_deberta(food_diary_entry)

#@st.cache_data
def get_result_from_chat_gpt3(food_diary_entry: str) -> pd.DataFrame:
    client = OpenAI(api_key=apikey)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "system", "content": "You are a dietitian. Categorize the information you receive, using a table format. The table should contain: food, portion size, units. Use one word or one number only. Ensure unique food names."},
            {"role": "user", "content": food_diary_entry}
        ],
        functions=[
            {
                "name": "get_food_breakdown",
                "description": "Return the keywords in the prompt which satisfy the criteria",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "Meal": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "a list of foods the prompt has."
                        },
                        "Meal_start_idx": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "start index for the corresponding food."
                        },
                        "Meal_end_idx": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "end index for the corresponding food."
                        },
                        "Amount": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "list of numbers, corresponding to the above foods. Put null if nothing found."
                        },
                        "Amount_start_idx": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "start index for the corresponding quantity."
                        },
                        "Amount_end_idx": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "end index for the corresponding quantity."
                        },
                        "Unit": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "letters or words following and corresponding to the numbers from above. Put null if nothing found."
                        },
                        "Unit_start_idx": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "start index for the corresponding units."
                        },
                        "Unit_end_idx": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "end index for the corresponding units."
                        }
                    },
                    "required": ["Meal","Meal_start_idx", 'Meal_end_idx', "Amount", "Amount_start_idx", "Amount_end_idx", "Unit", "Unit_start_idx", "Unit_end_idx"]
                }
            }
        ],
        function_call="auto",
        max_tokens=300
    )

    if completion.choices[0].message.function_call is None:
        df = pd.DataFrame(columns=["Meal", "Meal_start_idx", 'Meal_end_idx', "Amount", "Amount_start_idx", "Amount_end_idx", "Unit", "Unit_start_idx", "Unit_end_idx"])
        print(df)
        return df

    print("ChatGPT found this:", completion.choices[0].message.function_call.arguments)

    args = json.loads(completion.choices[0].message.function_call.arguments)

    return pd.DataFrame.from_dict(args, orient='columns')

def get_result_from_deberta(food_name: str) -> pd.DataFrame:
    pipe = pipeline("ner", model="davanstrien/deberta-v3-base_fine_tuned_food_ner")

    result = pipe(food_name)

    result = [entity for entity in result if entity['score'] >= 0.3]

    # Iterate over the results to merge consecutive rows with the same entity
    for i in range(len(result) - 1, 0, -1):
        current_entity = result[i]["entity"]
        previous_entity = result[i - 1]["entity"].split('-')[1]

        if current_entity.split('-')[1] == previous_entity:
            # Append the word from the row below to the "word" column
            result[i - 1]["word"] += result[i]["word"]

            # Update the "end" value of the first row with the "end" value of the row below
            result[i - 1]["end"] = result[i]["end"]

            # Delete the current row
            del result[i]

    # Lists to store information
    foods = []
    quantities = []
    units = []

    # Iterate over the resulting entities
    for entity in result:
        if "FOOD" in entity["entity"]:
            current_food = {"food": entity["word"], "food_start": entity["start"], "food_end": entity["end"]}
            foods.append(current_food)
        elif "QUANTITY" in entity["entity"]:
            current_quantity = {"quantity": entity["word"], "quantity_start": entity["start"], "quantity_end": entity["end"]}
            quantities.append(current_quantity)
        elif "UNIT" in entity["entity"]:
            current_unit = {"unit": entity["word"], "unit_start": entity["start"], "unit_end": entity["end"]}
            units.append(current_unit)

    # Create separate DataFrames for each type of information
    df_food = pd.DataFrame(foods)
    df_quantity = pd.DataFrame(quantities)
    df_unit = pd.DataFrame(units)

    # Check if df_quantity and df_unit are empty, and create them if needed
    if df_food.empty:
        df_food = pd.DataFrame(columns=["quantity", "quantity_start", "quantity_end"])

    if df_quantity.empty:
        df_quantity = pd.DataFrame(columns=["quantity", "quantity_start", "quantity_end"])

    if df_unit.empty:
        df_unit = pd.DataFrame(columns=["unit", "unit_start", "unit_end"])


    # Combine the DataFrames
    df_edited = pd.concat([df_food, df_quantity, df_unit], axis=1)

    # Fill NaN values with 0
    df_edited = df_edited.fillna(0)

    for i, rows in df_edited.iterrows():
        df_edited['food'][i] = str(df_edited['food'][i]).replace("▁"," ").strip().lower().capitalize()
        df_edited['quantity'][i] = str(df_edited['quantity'][i]).replace("▁"," ").strip().lower().capitalize()
        df_edited['unit'][i] = str(df_edited['unit'][i]).replace("▁"," ").strip()


    # Replace NaN, nan, and NaN with a specific non-null value (e.g., 0) across the entire DataFrame
    df_edited.replace({pd.NaT: 0, 'Nan': 0, 'nan': 0, 'NaN': 0}, inplace=True)
    df_edited = df_edited.fillna(0)

    # ["Meal", "Meal_start_idx", 'Meal_end_idx', "Amount", "Amount_start_idx", "Amount_end_idx", "Unit", "Unit_start_idx", "Unit_end_idx"]
    df_edited['Meal'] = df_edited['food'].astype(str)
    df_edited['Meal_start_idx'] = df_edited['food_start'].astype(int)
    df_edited['Meal_end_idx'] = df_edited['food_end'].astype(int)

    #df_edited['Amount'] = df_edited['quantity'].astype(float)
    df_edited['Amount_start_idx'] = df_edited['quantity_start'].astype(int)
    df_edited['Amount_end_idx'] = df_edited['quantity_end'].astype(int)

    df_edited['Unit'] = df_edited['unit'].astype(str)
    df_edited['unUnit_start_idxit_start'] = df_edited['unit_start'].astype(int)
    df_edited['Unit_end_idx'] = df_edited['unit_end'].astype(int)


    pd.set_option("mode.chained_assignment", None)

    print(f"\n\n\033[1m{food_name}\033[0m\n")

    return df_edited
