from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import recommendations
import os
from boto.s3.connection import S3Connection

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_APP_KEY')
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', "sqlite:///blog.db")
db = SQLAlchemy(app)

TMDB_API = os.getenv('TMDB_API')
TMDB_URL = "https://api.themoviedb.org/3/search/movie/"

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, unique=True, nullable=False)
    year = db.Column(db.Integer, unique=False, nullable=False)
    description = db.Column(db.Text, unique=False, nullable=False)
    rating = db.Column(db.Float, unique=False, nullable=False)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.Text, unique=False, nullable=False)
    img_url = db.Column(db.Text, unique=False, nullable=False)

    def __repr__(self):
        return '<Show %r>' % self.title

db.create_all()

class EditForm(FlaskForm):
    rating = StringField('Rating', validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddForm(FlaskForm):
    title = StringField('Move Title', validators=[DataRequired()])
    submit = SubmitField('Submit')

# new_show = Show (
#         title="Game of Thrones",
#         year=2011,
#         description="7 families across Westeros fight for the Iron Throne",
#         rating=8.7,
#         ranking=5,
#         review="Amazing start... let's not talk about the ending",
#         img_url="https://cdn.shopify.com/s/files/1/0006/6060/2935/products/gothoipossnw_530x@2x.jpg?v=1556694124"
#     )
#
# db.session.add(new_show)
# db.session.commit()

all_shows = []
all_recommendations = {}

@app.route("/")
def home():
    order = Show.query.order_by(Show.rating)
    i = Show.query.count()
    for show in order:
        show.ranking = i
        reco_list = recommendations.clean_data(show.title)
        if reco_list is not None:
            final_recommendations = recommendations.find_recommendations(reco_list[0], reco_list[1])
            all_recommendations[show.title] = final_recommendations
        else:
            all_recommendations[show.title] = ["None"]
        i -= 1
    return render_template("index.html", shows=order, recommendations=all_recommendations)

@app.route("/edit/<show_id>", methods=['GET', 'POST'])
def edit(show_id):
    current_show = Show.query.filter_by(id=show_id).first()
    form = EditForm()
    if form.validate_on_submit():
        current_show.rating = request.form["rating"]
        current_show.review = request.form["review"]
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', show=current_show, form=form)

@app.route("/delete")
def delete():
    show_id = request.args.get("show_id")
    show_to_delete = Show.query.get(show_id)
    db.session.delete(show_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add", methods=['GET', 'POST'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        add_title = request.form["title"]
        parameters = {
            "api_key": TMDB_API,
            "query": add_title,
        }
        response = requests.get(url=TMDB_URL, params=parameters)
        movie_results = response.json()["results"]
        return render_template('select.html', show_results=movie_results)
    return render_template('add.html', form=form)

@app.route("/find")
def find():
    if request.args.get("show_name") is not None:
        movie_name = request.args.get("show_name")
        parameters = {
            "api_key": TMDB_API,
            "query": movie_name,
        }
        response = requests.get(url=f"{TMDB_URL}", params=parameters)
        movie_results = response.json()["results"]
        print(movie_results[0]["original_title"])
        new_show = Show(
            title=movie_results[0]["original_title"],
            year=movie_results[0]["release_date"][:4],
            description=movie_results[0]["overview"],
            rating=0,
            ranking=0,
            review="None",
            img_url=f"https://image.tmdb.org/t/p/w500{movie_results[0]['backdrop_path']}"
        )
        db.session.add(new_show)
        db.session.commit()
        form = EditForm()
        return redirect(url_for('edit', show_id=new_show.id, show=new_show, form=form))


if __name__ == '__main__':
    app.run(debug=True)
