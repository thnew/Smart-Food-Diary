# streamlit-custom-component

Streamlit component that allows you to do X

## Installation instructions

```sh
pip install streamlit-custom-component
```

## Debug
```In the frontend folder (cd highlighted_textarea/frontend): npm run start```
```From the partent folder of this (cd ..): streamlit run highlighted_textarea/example.py```

## Usage instructions

```python
import streamlit as st

from highlighted_textarea import highlighted_textarea

value = highlighted_textarea()

st.write(value)
```
