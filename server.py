"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from datetime import datetime
from model import connect_to_db, db, User, Rating, Movie
from forms import RegistrationForm, LoginForm, RatingForm
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

BERATEMENT_MESSAGES = [
    "I suppose you don't have such bad taste after all.",
    "I regret every decision that I've ever made has brought me to listen to your opinion.",
    "Words fail me, as your taste in movies has clearly failed you.",
    "That movie is great. For a clown to watch. Idiot.",
    "Words cannot express the awfulness of your taste."
]


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
    # get user_id from session
    user_id = session.get("user_id")
    
    # get movie, format date, and calc average rating
    movie = Movie.query.get(movie_id)
    date = movie.released_at.strftime("%b-%d-%Y")
    scores = [r.score for r in movie.ratings]
    avg_rating = round(sum(scores)/len(scores))

    # get user_rating if it exists and user is logged in
    if user_id:
        user_rating = Rating.query.filter_by(movie_id=movie_id, user_id=user_id).first()
        if user_rating:
            user_rating = round(user_rating.score)
    else:
        user_rating = None
    
    # get prediction if user_rating doesn't exist and user is logged in
    prediction = None
    if (not user_rating) and user_id:
        user = User.query.get(user_id)
        if user:
            prediction = user.predict_rating(movie)
            if prediction:
                prediction = round(prediction)

    if prediction:
        effective_rating = prediction
    elif user_rating:
        effective_rating = user_rating
    else:
        effective_rating = None

    the_eye = (User.query.filter_by(email="the-eye@of-judgment.com").one())
    eye_rating = Rating.query.filter_by(user_id=the_eye.user_id, movie_id=movie.movie_id).first()

    if eye_rating is None:
        eye_rating = the_eye.predict_rating(movie)
    else:
        eye_rating = eye_rating.score
    
    if eye_rating and effective_rating:
        beratement = BERATEMENT_MESSAGES[abs(round(eye_rating) - effective_rating)]
    else:
        beratement = None

    return render_template(
        "movie_detail.html", 
        movie=movie, 
        date=date, 
        movie_avg=avg_rating, 
        ratings=movie.ratings, 
        user_rating=user_rating, 
        prediction=prediction,
        beratement=beratement
        )

@app.route('/movies/<movie_id>/rate', methods=["GET","POST"])
def rate_movie(movie_id):
    user_id = session.get("user_id")
    
    if not user_id:
        flash("Log in to rate movies", "warning")
        return redirect(url_for("movie_detail", movie_id=movie_id))
    
    movie = Movie.query.get(movie_id)
    

    form = RatingForm()
    
    if form.validate_on_submit():
        score = form.rating.data
        existing_rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if existing_rating == None:
            rating = Rating(movie_id=movie_id, user_id=user_id, score=score)
            db.session.add(rating)
        else:
            existing_rating.score = score
        db.session.commit()
        return redirect(url_for("movie_detail", movie_id=movie_id))

    return render_template("rate_movie.html", form=form, movie=movie)

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
