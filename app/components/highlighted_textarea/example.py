import streamlit as st
from highlighted_textarea import highlighted_textarea

# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run highlighted_textarea/example.py`

st.subheader("Example with custom component")

# Create an instance of our component with a constant `name` arg, and
# print its output value.

if "value" not in st.session_state:
    st.session_state.value = "2 glasses Fanta, 2 Cesars \nSalad and 1 Schnitzel and some chocolate"

st.write(st.session_state.value)

value = highlighted_textarea(st.session_state.value, labels=[(2, 20, '#f00'), (20, 45)])
st.markdown(f"Value: {value}")

if value:
    st.session_state.value = value
