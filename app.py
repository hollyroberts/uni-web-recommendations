from flask import Flask, session, render_template, redirect, request, jsonify, abort, send_from_directory, g
from flask_babel import Babel, gettext
import os
from db import Database

app = Flask(__name__, static_url_path='/static')
babel = Babel(app)

LANGUAGES = {
    'en': 'English',
    'es': 'Español',
    'se': 'Svenska'
}

# Babel functions
@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    if 'locale' in session:
        return session['locale']

    # otherwise try to guess the language from the user accept header the browser transmits
    return request.accept_languages.best_match(LANGUAGES.keys())

@app.before_request
def set_locale():
    g.locale = get_locale()
    g.languages = LANGUAGES

# Static routing/translations
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.route("/get_translations")
def translations():
    return jsonify({
        "no_genres": gettext("No genres"),
        "no_rating": gettext("No rating"),
        "delete": gettext("Delete"),
        "have_not_rated": gettext("You haven't rated any movies"),
        "error_deleting": gettext("Error deleting rating - this should never happen"),
        "error_rating": gettext("Error updating rating - this should never happen"),
        "loading_movies": gettext("Loading movies..."),
        "rating_deleted": gettext('Rating for "*" deleted'),
        "rating_updated": gettext('Rating for "*" updated to &/5'),
        "no_ratings_so_no_reccs": gettext("You haven't rated any movies yet, so no recommendations can be generated")
    })

# HTML pages
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

# Commands
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
    include_rated_movies = request.args.get('include_rated_movies') == 'true'
    page = int(request.args.get('page', 0))

    results = Database.search_movies(title, session['user']['id'], page, recommend, include_rated_movies)

    return jsonify(results)

@app.route("/recommendations")
def get_reccs():
    if 'user' not in session:
        return redirect('user.html')

    page = int(request.args.get('page', 0))
    include_rated_movies = request.args.get('include_rated_movies') == 'true'

    return jsonify(Database.get_reccs(session['user']['id'], page, include_rated_movies))

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

@app.route("/change_language")
def change_language():
    session['locale'] = request.args.get('locale')

    return redirect(request.referrer)

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
