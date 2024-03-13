import streamlit as st
import pandas as pd
from highlighted_textarea import highlighted_textarea

# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run highlighted_textarea/example.py`

st.subheader("Example with custom component")

result = highlighted_textarea(initial_value="2 glasses Fanta, 2 Cesars \nSalad and 1 Schnitzel and some chocolate", api_url="http://localhost:8501/", key="example")

st.write(result['value'])
st.dataframe(pd.DataFrame(result['dataframe']))
