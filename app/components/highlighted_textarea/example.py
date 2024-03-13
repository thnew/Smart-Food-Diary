import streamlit as st
import pandas as pd
from highlighted_textarea import highlighted_textarea

# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run highlighted_textarea/example.py`

st.subheader("Example with custom component")

# Create an instance of our component with a constant `name` arg, and
# print its output input_text.

if "input_text" not in st.session_state:
    st.session_state.input_text = "2 glasses Fanta, 2 Cesars \nSalad and 1 Schnitzel and some chocolate"

result = highlighted_textarea(initial_value=st.session_state.input_text, key="example")
print("RESULT",result)
st.write(result['value'])
st.dataframe(pd.DataFrame(result['dataframe']))

if result['value']:
    st.session_state.input_text = result['value']
