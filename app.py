from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/user.html')
def new_user():
    return render_template('user.html')

if __name__ == '__main__':
    app.add_url_rule('/favicon.ico',
                     redirect_to=url_for('static', filename='favicon.ico'))
    app.run()
