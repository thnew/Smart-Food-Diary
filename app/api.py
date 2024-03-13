import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from classes.get_nutrition_values import get_nutrition_values
from classes.extract_meals_from_text import extract_meals_from_input

app = FastAPI()

# Allowing all middleware is optional, but good practice for dev purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/analyze-text-input")
def analyzeMeals(text: str):
    """
    Analyzes given meal text
    """

    extracted_meals = extract_meals_from_input(text, "deberta-local")
    nutrition_values = get_nutrition_values(extracted_meals)

    response = {col: nutrition_values[col].to_list() for col in nutrition_values.columns}

    return response

@app.get("/")
def root():
    return {
        'greeting': 'Hello'
    }


# Run from root folder with this:
# uvicorn taxifare.api.fast:app --reload
