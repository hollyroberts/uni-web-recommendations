import sqlite3

import pandas
from flask import Flask, session, render_template, url_for, redirect, g, current_app

app = Flask(__name__, static_url_path='/static')

print("Loading movies")
csv_movies = pandas.read_csv("data/movies.csv")
# print("Loading ratings")
# csv_ratings = pandas.read_csv("data/ratings.csv")
print("CSV files loaded")

@app.route('/')
@app.route('/index.html')
def index():
    if 'user' not in session:
        return redirect('user.html')

    return render_template('index.html', session=session)

@app.route('/user.html')
def user_page():
    return render_template('user.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    pass

if __name__ == '__main__':
    # Todo init db
    app.run()
