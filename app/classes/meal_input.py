import pandas as pd
import streamlit as st
from streamlit_javascript import st_javascript
from io import StringIO

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
        set_to_local_storage(f'{self.id}_input_text', self.input_text)
        set_to_local_storage(f'{self.id}_parsed_meals', self.parsed_meals.to_json())

    def load_from_local_storage(self):
        self.input_text = get_from_local_storage(f'{self.id}_input_text')
        self.input_text = self.input_text if self.input_text else ''

        try:
            parsed_meals_serialized = get_from_local_storage(f'{self.id}_parsed_meals')
            self.parsed_meals = pd.read_json(StringIO(parsed_meals_serialized)) if parsed_meals_serialized else pd.DataFrame(columns=['meal_name', 'amount', 'unit'])
        except:
            pass

        return self

st.markdown('<style>.hide-next-elem, .hide-next-elem + * { display: none }</style>', unsafe_allow_html=True)

# TODO: Replace with cache or hide
def get_from_local_storage(k):
    st.write("<div class='hide-next-elem'></div>", unsafe_allow_html=True, )
    v = st_javascript(f"localStorage.getItem('{k}');")

    return v if v else None

def set_to_local_storage(k, v):
    st.write("<div class='hide-next-elem'></div>", unsafe_allow_html=True)
    st_javascript(f"localStorage.setItem('{k}', '{v}');")
