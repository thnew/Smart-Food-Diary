import streamlit as st
import pandas as pd
import json
import os
import string
import requests
from transformers import pipeline
from openai import OpenAI
from dotenv import load_dotenv
import time

import warnings
warnings.filterwarnings("ignore")

load_dotenv()
apikey = os.environ.get('OPENAPI_APIKEY')

# Split up input in rows and extract
def extract_meals_from_input(text: str, use_chat_gpt: bool) -> pd.DataFrame:
    # We process inputs line by line
    lines = text.split("\n")

    # Go through every row and parse the meal names, units and amounts of of them
    meals_df = pd.DataFrame(columns=['food', 'food_start', 'food_end', 'unit', 'unit_start', 'unit_end', 'quantity', 'quantity_start', 'quantity_end'])
    for row in lines:
        meals_df = pd.concat([meals_df, extract_meals_from_text(row, use_chat_gpt)])

    return meals_df.reset_index(drop=True)

def extract_meals_from_text(food_diary_entry: str, use_chat_gpt: bool) -> pd.DataFrame:
    if len(food_diary_entry) == 0:
        return pd.DataFrame(columns=['food', 'quantity', 'unit'])

    time = current_milli_time()
    df =(get_result_from_chat_gpt3(food_diary_entry)
         if use_chat_gpt else get_result_from_deberta(food_diary_entry))
    print("TIME TOTAL TO EXTRACT", current_milli_time() - time)

    columns_to_convert = ['food_start', 'food_end', 'quantity_start', 'quantity_end', 'unit_start', 'unit_end']
    df[columns_to_convert] = df[columns_to_convert].fillna(-1)
    df[columns_to_convert] = df[columns_to_convert].astype(int)

    return df

@st.cache_data
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
                        "food": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "a list of foods the prompt has."
                        },
                        "food_start": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "start index for the corresponding food."
                        },
                        "food_end": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "end index for the corresponding food."
                        },
                        "quantity": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "list of numbers, corresponding to the above foods. Put null if nothing found."
                        },
                        "quantity_start": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "start index for the corresponding quantity."
                        },
                        "quantity_end": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "end index for the corresponding quantity."
                        },
                        "unit": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "letters or words following and corresponding to the numbers from above. Put null if nothing found."
                        },
                        "unit_start": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "start index for the corresponding units."
                        },
                        "unit_end": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "end index for the corresponding units."
                        }
                    },
                    "required": ["food", "food_start", 'food_end', "quantity", "quantity_start", "quantity_end", "unit", "unit_start", "unit_end"]
                }
            }
        ],
        function_call="auto",
        max_tokens=300
    )

    if completion.choices[0].message.function_call is None:
        df = pd.DataFrame(columns=["food", "food_start", 'food_end', "quantity", "quantity_start", "quantity_end", "unit", "unit_start", "unit_end"])

        return df

    args = json.loads(completion.choices[0].message.function_call.arguments)

    return pd.DataFrame.from_dict(args, orient='columns')

#@st.cache_data
def get_result_from_deberta(text: str) -> pd.DataFrame:
    return ner_food_output(text.lower())

    response = None
    for attempts in range(1, 4):
        try:
            url = "https://ner-food-ctgsi4wqxa-ew.a.run.app/"
            params = {
                "text": text.lower()
            }

            response = requests.get(url, params).json()

            break
        except:
            print(f"Failed {attempts} times")

    if response is None:
        return pd.DataFrame(columns=["food", "food_start", 'food_end', "quantity", "quantity_start", "quantity_end", "unit", "unit_start", "unit_end"])

    return pd.DataFrame(response)

# Load the NER pipeline using a fine-tuned model for food entities
pipe = pipeline("ner", model="davanstrien/deberta-v3-base_fine_tuned_food_ner")

def ner_food_output(food_name):
    time = current_milli_time()

    print("TIME A", current_milli_time() - time)
    x = current_milli_time()

    # Get the NER results for the given food_name
    result = pipe(food_name)

    # Filter entities with confidence score >= 0.3
    result = [entity for entity in result if entity['score'] >= 0.3]

    # Iterate over the results to merge consecutive rows with the same entity
    for i in range(len(result) - 1, 0, -1):
        current_entity = result[i]["entity"]
        previous_entity = result[i - 1]["entity"].split('-')[1]

        # Merge consecutive rows with the same entity
        if current_entity.split('-')[1] == previous_entity:
            if current_entity.split('-')[0] == "U":
                None
            if current_entity.split('-')[0] == "I" or current_entity.split('-')[0] == "L":
                # Append the word from the row below to the "word" column
                result[i - 1]["word"] += result[i]["word"]

                # Update the "end" value of the first row with the "end" value of the row below
                result[i - 1]["end"] = result[i]["end"]

                # Delete the current row
                del result[i]

    # Identify sentence boundaries based on start and end indices
    sentences=[]
    end_sentence = len(food_name)

    for i in range(len(result) - 1, 0, -1):
        current_entity = result[i]["entity"]
        previous_entity = result[i - 1]["entity"].split('-')[1]

        if result[i]["start"] != result[i-1]["end"]:
            start_index = result[i-1]["end"]
            end_index = result[i]["start"]

            # Check for conjunctions or punctuation to determine sentence boundaries
            if ' and' in food_name[start_index:end_index] or any([punc in food_name[start_index:end_index] for punc in string.punctuation]):
                sentences.append(end_sentence)
                end_sentence = start_index

    sentences.append(end_sentence)
    sentences = sentences[::-1]

    # Create a DataFrame from the NER results
    a=pd.DataFrame(result)
    output = []

    # Extract rows corresponding to each identified sentence
    for end in sentences:
        i = a[a["end"]==end].index[0]
        output.append([])
        for row in range(i+1):
            output[-1].append(a.loc[row].to_dict())
        a = a.loc[i+1:].reset_index(drop=True)

    print("TIME B", current_milli_time() - time)
    x = current_milli_time()

    # Concatenate cleaned text output (function used) for each sentence
    result = pd.concat([clean_text(o) for o in output])

    print("TIME C", current_milli_time() - time)
    x = current_milli_time()
    result.reset_index(drop=True, inplace=True)

    return result

def clean_text(result):

    # Lists to store information
    foods = []
    quantities = []
    units = []

    # Iterate over the resulting entities and append the information
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

    # Check if DataFrames are empty, and create them if needed
    if df_food.empty:
        df_food = pd.DataFrame(columns=["quantity", "quantity_start", "quantity_end"])

    if df_quantity.empty:
        df_quantity = pd.DataFrame(columns=["quantity", "quantity_start", "quantity_end"])

    if df_unit.empty:
        df_unit = pd.DataFrame(columns=["unit", "unit_start", "unit_end"])


    # Combine the DataFrames
    df_edited = pd.concat([df_food, df_quantity, df_unit], axis=1)

    # Fill NaN values with -1
    df_edited = df_edited.fillna(-1)

    # Clean the text
    for i, rows in df_edited.iterrows():
        df_edited['food'][i] = str(df_edited['food'][i]).replace("▁"," ").strip().lower().capitalize()
        df_edited['quantity'][i] = str(df_edited['quantity'][i]).replace("▁"," ").strip().lower().capitalize()
        df_edited['unit'][i] = str(df_edited['unit'][i]).replace("▁"," ").strip()


    # Replace NaN, nan, and NaN with a specific non-null value (e.g., -1) across the entire DataFrame
    df_edited.replace({pd.NaT: -1, 'Nan': -1, 'nan': -1, 'NaN': -1}, inplace=True)
    df_edited = df_edited.fillna(-1)

    # Change type for each columns
    df_edited['food'] = df_edited['food'].astype(str)
    df_edited['food_start'] = df_edited['food_start'].astype(int)
    df_edited['food_end'] = df_edited['food_end'].astype(int)

    df_edited['quantity_start'] = df_edited['quantity_start'].astype(int)
    df_edited['quantity_end'] = df_edited['quantity_end'].astype(int)

    df_edited['unit'] = df_edited['unit'].astype(str)
    df_edited['unit_start'] = df_edited['unit_start'].astype(int)
    df_edited['unit_end'] = df_edited['unit_end'].astype(int)

    # Ignore warnings
    pd.set_option("mode.chained_assignment", None)

    return df_edited


def current_milli_time():
    return round(time.time() * 1000)
