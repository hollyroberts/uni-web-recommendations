import pandas
import sqlite3, time
from flask import Flask, session, render_template, redirect, request

from db import Database

app = Flask(__name__, static_url_path='/static')

start = time.time()
with sqlite3.connect("database.db") as db:
    print("Loading movies")
    movies = pandas.read_sql("SELECT id, title FROM movies", db)
    print(f"Loaded movies in {round(time.time() - start, 1)} seconds")

    print("Loading ratings")
    print("This will take a while (about a minute) and take a fair amount of memory")
    ratings = pandas.read_sql("SELECT user_id, movie_id, rating_score FROM ratings", db)
    print(f"Loaded ratings in {round(time.time() - start, 1)} seconds")
    print("Done")

print(movies.head())
print(ratings.head())

users = Database.get_users()

@app.route('/')
@app.route('/index.html')
def index():
    if 'user' not in session:
        return redirect('user.html')

    return render_template('index.html', session=session)

@app.route('/user.html')
def user_page():
    return render_template('user.html', users=users)

@app.route('/create_user', methods=['POST'])
def add_user():
    username = request.form['username']
    session['user'] = Database.add_user(username)

    return redirect('index.html')

@app.route("/select_user", methods=['POST'])
def change_user():
    user_id = request.form['user_id']

    session['user'] = Database.get_user(user_id)

    return redirect('index.html')

@app.route("/clear_session")
def clear_session():
    session.clear()

    return redirect('user.html')

@app.route("/search_movies", methods=['GET'])
def search_movies():
    if 'user' not in session:
        return redirect('user.html')

    # Retrieve args from request
    title = request.args.get('title')
    recommend = request.args.get('recommend')

    Database.search_movies(title)

    return '', 200

if __name__ == '__main__':
    app.secret_key = 'Movies'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run()
