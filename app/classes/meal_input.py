import pandas as pd
import streamlit as st

class MealInput:
    '''
    Represent breakfast, lunch and dinner input
    '''
    def __init__(self, id: str, title: str, input_text: str = '', parsed_meals: pd.DataFrame = None):
        self.id = id
        self.title = title
        self.value = input_text
        self.extracted_meals = pd.DataFrame(columns=['meal_name', 'amount', 'unit']) if parsed_meals is None else parsed_meals

    def store_in_cache(self):
        st.query_params[self.id] = self.value

    def load_from_cache(self):
        self.value = st.query_params.get(self.id)
        self.value = self.value if self.value else ''

        return self
