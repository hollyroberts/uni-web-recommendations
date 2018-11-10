import pandas
from flask import Flask, session, render_template, url_for, redirect, g, current_app, request

from db import Database

app = Flask(__name__, static_url_path='/static')

print("Loading movies")
csv_movies = pandas.read_csv("data/movies.csv")
# print("Loading ratings")
# csv_ratings = pandas.read_csv("data/ratings.csv")
print("CSV files loaded")

users = Database.get_users()
print(users)

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
    user_id = Database.add_user(username)

    session['user'] = {
        "id": user_id,
        "name": username
    }

    return redirect('index.html')

if __name__ == '__main__':
    app.secret_key = 'Movies'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run()
