import streamlit as st
import pandas as pd
import json
import os
import string
from transformers import pipeline
from openai import OpenAI
from dotenv import load_dotenv

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

    df =(get_result_from_chat_gpt3(food_diary_entry)
         if use_chat_gpt else get_result_from_deberta(food_diary_entry))

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

@st.cache_data
def get_result_from_deberta(text: str) -> pd.DataFrame:
    output = []

    for food, i in split_text(text):
        df = ner_food(food)
        df.iloc[:,1:]
        final = pd.concat(output)

    return final

def ner_food(result):
    # Lists to store information
    foods = []
    quantities = []
    units = []
    print("RESULTR", result)

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
    df_edited = df_edited.fillna(-1)

    for i, rows in df_edited.iterrows():
        df_edited['food'][i] = str(df_edited['food'][i]).replace("▁"," ").strip().lower().capitalize()
        df_edited['quantity'][i] = str(df_edited['quantity'][i]).replace("▁"," ").strip().lower().capitalize()
        df_edited['unit'][i] = str(df_edited['unit'][i]).replace("▁"," ").strip()


    # Replace NaN, nan, and NaN with a specific non-null value (e.g., 0) across the entire DataFrame
    df_edited.replace({pd.NaT: -1, 'Nan': -1, 'nan': -1, 'NaN': -1}, inplace=True)
    df_edited = df_edited.fillna(-1)

    df_edited['food'] = df_edited['food'].astype(str)
    df_edited['food_start'] = df_edited['food_start'].astype(int)
    df_edited['food_end'] = df_edited['food_end'].astype(int)

    #df_edited['quantity'] = df_edited['quantity'].astype(float)
    df_edited['quantity_start'] = df_edited['quantity_start'].astype(int)
    df_edited['quantity_end'] = df_edited['quantity_end'].astype(int)

    df_edited['unit'] = df_edited['unit'].astype(str)
    df_edited['unit_start'] = df_edited['unit_start'].astype(int)
    df_edited['unit_end'] = df_edited['unit_end'].astype(int)


    pd.set_option("mode.chained_assignment", None)

    #print(f"\n\n\033[1m{food_name}\033[0m\n")

    return df_edited

def split_text(food_name):
    pipe = pipeline("ner", model="davanstrien/deberta-v3-base_fine_tuned_food_ner")

    result = pipe(food_name)

    result = [entity for entity in result if entity['score'] >= 0.3]

    # Iterate over the results to merge consecutive rows with the same entity
    sentences=[]
    end_sentence = len(food_name)

    for i in range(len(result) - 1, 0, -1):
        current_entity = result[i]["entity"]
        previous_entity = result[i - 1]["entity"].split('-')[1]

        if result[i]["start"] != result[i-1]["end"]:
            start_index = result[i-1]["end"]
            end_index = result[i]["start"]

            if ' and' in food_name[start_index:end_index] or any([punc in food_name[start_index:end_index] for punc in string.punctuation]):
                sentences.append((food_name[end_index:end_sentence],end_index))
                end_sentence = start_index
                #split da dataframe para uma variável? depois corro a função na variável e junto os outputs das variáveis existentes?
                #pré-definição de 10 variáveis? Mesmo com NaN posso depois faço drop dos NaN...
    sentences.append((food_name[0:end_sentence],0))

    return sentences[::-1]
