# Smart-Food-Diary

## Basic overview over the project (everyone can edit in that whiteboard):
https://miro.com/app/board/uXjVNlDuSEw=/?share_link_id=62044369956

## pyenv environment is called “smart_food_diary”
``pyenv local smart_food_diary``

## Run Streamlit app:
``streamlit run app/app.py``


# Problem:
Writing food diaries is time consuming for the clients. Analysing the hand written diaries is time consuming for the coaches. The regular calorie counting apps are too time consuming for the client. A solution is needed that saves time for both parties. 

# Process:
1. Data sourcing. We needed to find the right datatset that had a large amount of meals with their calories and macronutrients
2. Data processing - cleaning the data and processing it in a format that allowed for a more accurate use of the language model
3. Learning and choosing an NLP model - we tried several language models, including Word2Vec, roberta and ChatGPT prompt engineering.
5. Integration of the final product into the Streamlit app

# Limitations:
It's a good proof of concept, but:/
Accucarcy of the output can be improved/
A different language model might perform better


### Tech stack used (not exhaustive):
Jupyter notebooks/
Pandas/
Numpy/
Scikit-learn/
Tensorflow/
NLTK/
Streamlit/
