"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from datetime import datetime
from model import connect_to_db, db, User, Rating, Movie
from forms import RegistrationForm, LoginForm
from sqlalchemy.sql import func

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined

app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")

@app.route('/users')
def user_list():
    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/users/<user_id>')
def user_detail(user_id):
    user = User.query.get(user_id)
    user_ratings = Rating.query.join(Movie, Rating.movie_id==Movie.movie_id).add_columns(Movie.title.label("title"), Rating.score.label("score")).filter(Rating.user_id==user.user_id).all()
    user_avg = Rating.query.with_entities(func.avg(Rating.score)).filter(Rating.user_id==user.user_id).first()
    user_avg = round(user_avg[0])
    return render_template("user_detail.html", user=user, user_avg=user_avg,ratings=user_ratings)

@app.route('/movies')
def movie_list():
    movies = Movie.query.order_by('title').all()
    return render_template("movie_list.html", movies=movies)

@app.route('/movies/<movie_id>')
def movie_detail(movie_id):
    movie = Movie.query.get(movie_id)
    movie_ratings = Rating.query.join(User, Rating.user_id==User.user_id).add_columns(User.email.label('email'), Rating.score.label('score')).filter(Rating.movie_id==Movie.movie_id).all()
    date = movie.released_at.strftime("%b-%d-%Y")
    movie_avg = Rating.query.with_entities(func.avg(Rating.score)).filter(Rating.movie_id==movie.movie_id).first()
    movie_avg = round(movie_avg[0])
    return render_template("movie_detail.html", movie=movie, date=date, movie_avg=movie_avg, ratings=movie_ratings)

@app.route('/register', methods=["GET","POST"])
def register():
    if session.get("user_id"):
        current_user = User.query.get(session.get("user_id"))
        flash("You are already logged in as " + current_user.email, "DANGER")
    
    form = RegistrationForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        age = form.age.data
        zipcode = form.zipcode.data

        user = User(email=email, password=password, age=age, zipcode=zipcode)
        db.session.add(user)
        db.session.commit()
        flash("You are registerd","success")
        return redirect(url_for("login"))
    
    return render_template("register.html", form=form)

@app.route('/login', methods=["GET","POST"])
def login():
    if session.get("user_id"):
        current_user = User.query.get(session.get("user_id"))
        flash("You are already logged in as " + current_user.email, "DANGER")
    
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.check_password(form.password.data):
            session["user_id"] = user.user_id
            flash("Logged in successfully", "success")
            return redirect(url_for('index'))
        else:
            flash("Incorrect Password", "error")
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
