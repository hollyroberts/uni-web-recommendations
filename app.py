from flask import Flask, session, render_template, redirect, request, jsonify, abort, send_from_directory
import os
from db import Database

app = Flask(__name__, static_url_path='/static')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.route('/')
@app.route('/index.html')
def index_page():
    if 'user' not in session:
        return redirect('user.html')

    return render_template('index.html', session=session)

@app.route('/user_ratings.html')
def user_ratings_page():
    if 'user' not in session:
        return redirect('user.html')

    Database.get_movie_ratings_for_user(session['user']['id'])
    return render_template('user_ratings.html', session=session)

@app.route('/user.html')
def user_page():
    return render_template('user.html', users=Database.get_users(), max_user_id=Database.number_of_users())

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

@app.route("/search_movies")
def search_movies():
    if 'user' not in session:
        return redirect('user.html')

    # Retrieve args from request
    title = request.args.get('title')
    recommend = request.args.get('recommend') == 'true'
    page = int(request.args.get('page', 0))

    results = Database.search_movies(title, session['user']['id'], page, recommend)

    return jsonify(results)

@app.route("/recommendations")
def get_reccs():
    if 'user' not in session:
        return redirect('user.html')

    page = int(request.args.get('page', 0))

    return jsonify(Database.get_reccs(session['user']['id'], page))

@app.route("/ratings")
def get_ratings():
    if 'user' not in session:
        return redirect('user.html')

    return jsonify(Database.get_movie_ratings_for_user(session['user']['id']))

@app.route("/delete_rating", methods=['POST'])
def delete_rating():
    if 'user' not in session:
        return redirect('user.html')

    user_id = session['user']['id']
    movie_id = int(request.form['movie_id'])
    Database.delete_rating(user_id, movie_id)

    return '', 200

@app.route("/update_recommendation", methods=['POST'])
def update_recc():
    if 'user' not in session:
        return redirect('user.html')

    user_id = session['user']['id']
    movie_id = int(request.form['movie_id'])
    rating = float(request.form['rating'])

    # Validate rating
    if rating < 0.5 or rating > 5.0 or rating % 0.5 != 0:
        return abort(400)

    Database.update_rating(user_id, movie_id, rating)

    return '', 200

if __name__ == '__main__':
    app.secret_key = 'Movies'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run()
