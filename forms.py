from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Length, Email

class MovieSearchForm(FlaskForm):
    lang1 = StringField('Language 1', validators=[InputRequired()])
    lang2 = StringField('Language 2', validators=[InputRequired()])