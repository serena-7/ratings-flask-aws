from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, SubmitField, IntegerField, RadioField
from wtforms.validators import InputRequired, DataRequired, EqualTo, Length, ValidationError
from model import User

class RegistrationForm(FlaskForm):
    email = StringField("Email", 
                            validators=[
                                InputRequired("Input is required!"),
                                DataRequired("Data is required!"),
                                Length(max=64, message="email cannot be more than 64 characters")
                            ])
    password = PasswordField("Password",
                            validators=[
                                InputRequired("Input is required!"),
                                DataRequired("Data is required!"),
                                EqualTo("password_confirm", message="passwords must match")
                            ])
    
    password_confirm = PasswordField("Confirm Password",
                            validators=[
                                InputRequired("Input is required!"),
                                DataRequired("Data is required!")
                            ])
    age = IntegerField("Age")
    zipcode = StringField("ZipCode")
    submit = SubmitField("Register")

    def validate_email(self, email):
        if User.query.filter_by(email=self.email.data).first():
            raise ValidationError('Your email has been registered already!')

class LoginForm(FlaskForm):
    email = StringField("Email",
                            validators=[
                                InputRequired("Input is required!"),
                                DataRequired("Data is required!")
                            ])
    password = PasswordField("Password",
                            validators=[
                                InputRequired("Input is required!"),
                                DataRequired("Data is required!")
                            ])
    submit = SubmitField("LogIn")

    def validate_email(self, email):
        if User.query.filter_by(email=self.email.data).first() is None:
            raise ValidationError("Email is not registered!")

class RatingForm(FlaskForm):
    rating = RadioField('rating', choices=[
        (5,'☆'),
        (4,'☆'),
        (3,'☆'),
        (2,'☆'),
        (1,'☆')], 
        validators=[
            InputRequired("Input is required!"),
            DataRequired("Data is required")
        ])
    submit = SubmitField("Submit Rating")