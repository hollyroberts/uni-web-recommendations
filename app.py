import pandas
from flask import Flask, session, render_template, redirect, request

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

if __name__ == '__main__':
    app.secret_key = 'Movies'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run()
