import pandas as pd
import streamlit as st

class MealInput:
    '''
    Represent breakfast, lunch and dinner input
    '''
    def __init__(self, id: str, title: str, input_text: str = '', parsed_meals: pd.DataFrame = None):
        self.id = id
        self.title = title
        self.input_text = input_text
        self.parsed_meals = pd.DataFrame(columns=['meal_name', 'amount', 'unit']) if parsed_meals is None else parsed_meals

    def store_in_local_storage(self):
        st.query_params[self.id] = self.input_text

    def load_from_cache(self):
        self.input_text = st.query_params.get(self.id)
        self.input_text = self.input_text if self.input_text else ''

        return self
