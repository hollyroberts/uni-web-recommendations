import sqlite3

from flask import Flask, session, render_template, url_for, redirect, g, current_app

app = Flask(__name__)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

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
    print(init_db())
    print("HELLO")

    app.add_url_rule('/favicon.ico',
                     redirect_to=url_for('static', filename='favicon.ico'))
    app.run()
