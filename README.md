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
2. data processing - cleaning the data and processing it in a format that allowed for a more accurate use of the Word2Vec model
3. Learning and choosing an NLP model - we tried several language models, including Word2Vec, roberta and ChatGPT prompt engineering.
5. Integration of the final product into the Streamlit app

# Useful insights:
Some things a client may decide to do with these findings:
1. If they have a promotion or something important they want their customers to read, they need to attach it to the top viewed pages.
For example 'Blog', 'About us', 'Upcoming courses' pages, got the least amount of views. So if there's any important information on those pages, it won't be seen by many customers.
2. If the client wants to optimise their website, they can look at the best and worst performing pages and decide whether they want to remove some pages that don't perform well and focus their efforts on those that do.
3. If the client wants to direct the customer to a certain page (e.g.'Checkout'), they can observe how long it takes a customer to get to the Checkout page. Maybe the website is not intuitive enough, so the client may need to spend some time on improving their UX.


### Tech stack used (not exhaustive):
Jupyter notebooks/
Pandas/
Numpy/
Scikit-learn/
Tensorflow/
NLTK/
Streamlit/
