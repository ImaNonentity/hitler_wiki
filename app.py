import os

from flask import Flask, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from connection import DATABASE_URL
from main_logic import Searcher
from forms import AddPageForm


app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config['DEBUG'] = True

db = SQLAlchemy(app)

import models

migrate = Migrate(app, db)

@app.route('/greeting')
def greeting():
    return render_template('greeting.html')

@app.errorhandler(404)
def not_found(e):
  return render_template("404.html")

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def main_page():
    models.User.remember_user(request.remote_addr)
    search_form = AddPageForm(csrf_enabled=False)
    if search_form.validate_on_submit():
        search_task = Searcher(
            start=search_form.start.data,
            goal=search_form.goal.data
        )
        search_task.search()
        return render_template('findhi.html', loading_bar=False, form=AddPageForm())
    return render_template('findhi.html', loading_bar=True, form=AddPageForm())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)



