import pandas as pd

class MealInput:
    '''
    Represent breakfast, lunch and dinner input
    '''
    def __init__(self, id: str, title: str, input_text: str = '', parsed_meals: pd.DataFrame = None):
        self.id = id
        self.title = title
        self.input_text = input_text
        self.parsed_meals = pd.DataFrame(columns=['meal_name', 'amount', 'unit']) if parsed_meals is None else parsed_meals
