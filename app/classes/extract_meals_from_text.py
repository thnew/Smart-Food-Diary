import streamlit as st
import pandas as pd
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
apikey = os.environ.get('OPENAPI_APIKEY')

# Split up input in rows and extract
def extract_meals_from_input(text: str) -> pd.DataFrame:
    rows = text.split("\n")

    # Go through every row and parse the meal names, units and amounts of of them
    meals = pd.DataFrame(columns=['Meal', 'Amount', 'Unit'])
    for row in rows:
        meals = pd.concat([meals, extract_meals_from_text(row)])

    return meals.reset_index(drop=True)

def extract_meals_from_text(food_diary_entry: str) -> pd.DataFrame:
    if len(food_diary_entry) == 0:
        return pd.DataFrame(columns=['Meal', 'Amount', 'Unit'])

    return get_result_from_chat_gpt3(food_diary_entry)

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
                            "description": "start index for the corresponding food. Put null if nothing found."
                        },
                        "Meal_end_idx": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "end index for the corresponding food. Put null if nothing found."
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
                            "description": "start index for the corresponding quantity. Put null if nothing found."
                        },
                        "Amount_end_idx": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "end index for the corresponding quantity. Put null if nothing found."
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
                            "description": "start index for the corresponding units. Put null if nothing found."
                        },
                        "Unit_end_idx": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            },
                            "description": "end index for the corresponding units. Put null if nothing found."
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
        return pd.DataFrame(columns=["Meal", "Meal_start_idx", 'Meal_end_idx', "Amount", "Amount_start_idx", "Amount_end_idx", "Unit", "Unit_start_idx", "Unit_end_idx"])

    print("ChatGPT found this:", completion.choices[0].message.function_call.arguments)

    args = json.loads(completion.choices[0].message.function_call.arguments)

    return pd.DataFrame.from_dict(args, orient='columns')
