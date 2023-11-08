from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FloatField
from wtforms.validators import DataRequired, Email, Length


class SearchBookForm(FlaskForm):

    book_name = StringField("Search by Name")


class RegistrationForm(FlaskForm):
    """Form for adding users."""

    username = StringField('user_id', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('user_id', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class EditForm(FlaskForm):
    """Form for editing/updating user information"""

    username = StringField('user_id', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
