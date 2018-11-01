from flask import Flask, session, render_template, url_for, redirect

app = Flask(__name__)


@app.route('/')
@app.route('/index.html')
def index():
    if 'user' not in session:
        return redirect('user.html')

    return render_template('index.html')

@app.route('/user.html')
def new_user():
    return render_template('user.html')

if __name__ == '__main__':
    app.add_url_rule('/favicon.ico',
                     redirect_to=url_for('static', filename='favicon.ico'))
    app.run()
