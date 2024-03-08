import pandas as pd

# Split up input in rows and extract
def extract_meals_from_input(text: str) -> pd.DataFrame:
    rows = text.split("\n")

    # Go through every row and parse the meal names, units and amounts of of them
    meals = pd.DataFrame(columns=['Meal', 'Amount', 'Unit'])
    for row in rows:
        meals = pd.concat([meals, extract_meals_from_text(row)])

    return meals.reset_index(drop=True)

def extract_meals_from_text(text: str) -> pd.DataFrame:
    if len(text) == 0:
        return pd.DataFrame(columns=['Meal', 'Amount', 'Unit'])

    # TODO: Replace with AI

    return pd.DataFrame({
        'Meal': [text],
        'Amount': ['1'],
        'Unit': ['piece'],
    })
