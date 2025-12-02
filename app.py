
from flask import Flask, render_template, request
import pickle
import numpy as np
import difflib
import re

popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['post'])
def recommend():
    user_input = request.form.get('user_input')

    if not user_input or user_input.strip() == "":
        return render_template('recommend.html', error="Please enter a book title.")

    import difflib

    book_titles = pt.index.tolist()
    closest_matches = difflib.get_close_matches(user_input, book_titles, n=1)

    if not closest_matches:
        return render_template('recommend.html', error="Book not found. Please try another title.")

    book_title = closest_matches[0]
    index = pt.index.get_loc(book_title)

    similar_items = sorted(
        list(enumerate(similarity_scores[index])),
        key=lambda x: x[1],
        reverse=True
    )[1:5]

    data = []
    for i in similar_items:
        item = []
        title_to_find = re.escape(pt.index[i[0]])
        temp_df = books[books['Book-Title'].str.contains(title_to_find, case=False, na=False, regex=True)]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        data.append(item)

    return render_template('recommend.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)