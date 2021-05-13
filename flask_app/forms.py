from flask_app.models import Users, Movements

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    IntegerField,
    SelectField,
    TextAreaField,
    BooleanField,
    SelectMultipleField,
)
from wtforms.fields.html5 import DateField

from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
)
from datetime import date, datetime


class RegistrationForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    username = StringField(
        "username", validators=[DataRequired(), Length(min=6, max=20)]
    )
    email = StringField("email", validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired()])
    password_confirm = PasswordField(
        "confirm password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("register")

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "Username already taken please choose a different one."
            )

    def validate_email(self, email):
        email = Users.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError(
                "An account with this email already exists please Login in or use another email"
            )


class PasswordReset(FlaskForm):
    password = PasswordField("password", validators=[DataRequired()])
    password_confirm = PasswordField(
        "confirm password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("register")


class LoginForm(FlaskForm):
    email = StringField("email", validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired()])
    remember = BooleanField("remember me")
    submit = SubmitField("login")


class ResetRequest(FlaskForm):
    username = StringField(
        "username", validators=[DataRequired(), Length(min=6, max=20)]
    )
    email = StringField("email", validators=[DataRequired(), Email()])
    submit = SubmitField("submit")


class ScoreTimeComponenets(FlaskForm):
    minutes = IntegerField("Minutes")
    seconds = IntegerField("Seconds")
    score_type = SelectField(
        "type", choices=[("time", "time")], validators=[DataRequired()]
    )
    notes = TextAreaField("notes")
    submit = SubmitField("score")


class ScoreComponents(FlaskForm):
    score = IntegerField("score", validators=[DataRequired()])
    score_type = SelectField(
        "type", choices=[("reps", "reps"), ("lbs", "lbs")], validators=[DataRequired()]
    )
    notes = TextAreaField("notes")
    submit = SubmitField("score")


class CreateWorkout(FlaskForm):
    date = DateField("Date", default=datetime.today().date)
    user = SelectField(
        "Athlete",
        choices=[
            (int(athlete.id), (athlete.username, athlete.id))
            for athlete in Users.query.all()
        ],
    )
    submit = SubmitField("Submit")


class CreateComponent(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("description", validators=[DataRequired()])
    is_test = BooleanField("Test?")
    is_benchmark = BooleanField("Benchmark?")
    movements = SelectMultipleField(
        "movements",
        choices=[
            (movement, movement)
            for movement in Movements.query.order_by(Movements.name).all()
        ],
        validators=[DataRequired()],
    )
    score_type = SelectField(
        "Type", choices=[("reps", "reps"), ("lbs", "lbs"), ("time", "time")]
    )
    submit = SubmitField("submit")


class CreateMovement(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    upper = BooleanField("upper")
    lower = BooleanField("lower")
    full = BooleanField("full")
    push = BooleanField("push")
    pull = BooleanField("pull")
    total = BooleanField("total")
    kind = SelectField(
        "movement type",
        choices=[
            ("Weightlifting", "weightlifting "),
            ("Gymnastics", "gymnastics"),
            ("Monostructural", "monostructural"),
        ],
    )
    submit = SubmitField("submit")


class UpdateMovement(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    upper = BooleanField("upper")
    lower = BooleanField("lower")
    full = BooleanField("full")
    push = BooleanField("push")
    pull = BooleanField("pull")
    total = BooleanField("total")
    kind = SelectField(
        "movement type",
        choices=[
            ("Weightlifting", "weightlifting "),
            ("Gymnastics", "gymnastics"),
            ("Monostructural", "monostructural"),
        ],
    )
    submit = SubmitField("submit")


class AccountUpdate(FlaskForm):
    name = StringField("name")
    username = StringField("username")
    email = StringField("username", validators=[Email()])
    profile_pic = FileField("Update Profile Pic")
    submit = SubmitField("update")

class AddTestScore(FlaskForm):
    move = SelectField('Movement',choices=[(movement.id, movement)for movement in Movements.query.order_by(Movements.name).all()], validators = [DataRequired()])
    score = IntegerField('Score', validators = [DataRequired()])
    score_type = SelectField("Type", choices=[("reps", "reps"), ("lbs", "lbs"), ("time", "time")])
    date = DateField("Date", default=datetime.today().date)
    notes = TextAreaField('Notes')
    submit = SubmitField('Submit')