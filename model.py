"""Models and database functions for Ratings project."""
# import os
# from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import correlation
from config import PG_URI
# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)
# load_dotenv()

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        return f"<User user_id={self.user_id} email={self.email}>"

    def check_password(self, password_input):
        return self.password == password_input

    def similarity(self, other):
        """Return Pearson rating for user compared to other user"""
        u_ratings = {}
        paired_ratings = []

        for r in self.ratings:
            u_ratings[r.movie_id] = r
        for r in other.ratings:
            u_rating = u_ratings.get(r.movie_id)
            if u_rating:
                paired_ratings.append((u_rating.score, r.score))

        if paired_ratings:
            return correlation.pearson(paired_ratings)
        else:
            return 0.0

    def predict_rating(self, movie):
        """Predict a user's rating of a movie"""
        other_ratings = movie.ratings
        other_users = [r.user for r in other_ratings]

        similarities = [
            (self.similarity(r.user), r)
            for r in other_ratings
        ]

        similarities.sort(key=lambda x: x[0], reverse=True)

        similarities = [(sim, r) for sim, r in similarities if sim > 0]

        if not similarities:
            return None

        numerator = sum([r.score * sim for sim, r in similarities])
        denominator = sum([sim for sim, r in similarities])

        return numerator / denominator
        # similarities.sort(reverse=True)
        # sim, rating = similarities[0]

        # return rating.score * sim

# Put your Movie and Rating model classes here.


class Movie(db.Model):

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)
    imdb_url = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f"<Movie movie_id={self.movie_id} title={self.title}>"


class Rating(db.Model):

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey(
        "movies.movie_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "users.user_id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    user = db.relationship("User", backref=db.backref(
        "ratings", order_by=rating_id))
    movie = db.relationship("Movie", backref=db.backref(
        "ratings", order_by=rating_id))

    def __repr__(self):
        return f"<Rating rating_id={self.rating_id} movie_id={self.movie_id} user_id={self.user_id} score={self.score}>"
##############################################################################
# Helper functions


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = PG_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")
