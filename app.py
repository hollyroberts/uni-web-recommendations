import sqlite3

import pandas
from flask import Flask, session, render_template, url_for, redirect, g, current_app

app = Flask(__name__)

print("Loading movies")
csv_movies = pandas.read_csv("data/movies.csv")
#print("Loading ratings")
#csv_ratings = pandas.read_csv("data/ratings.csv")
print("CSV files loaded")


@app.route('/')
@app.route('/index.html')
def index():
    if 'user' not in session:
        return redirect('user.html')

    return render_template('index.html', session=session)

@app.route('/user.html')
def new_user():
    return render_template('user.html')

if __name__ == '__main__':
    # Todo init db
    app.run()
