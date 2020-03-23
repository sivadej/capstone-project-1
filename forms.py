from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, BooleanField
from wtforms.validators import InputRequired, Length, Email, NumberRange

audio_langs = ['English','Spanish','Cantonese','Brazilian','Tagalog','French','German','Mandarin','Arabic','Korean','Slovak','Thai','Turkish','Vietnamese']
sub_langs = ['English','Spanish','Brazilian','Tagalog','French','German','Arabic','Korean','Slovak','Thai','Chinese','Turkish','Vietnamese']

def get_tuples(langs):
    list_of_lang_tuples=[]
    langs.sort()
    for lang in langs:
        list_of_lang_tuples.append((lang,lang))
    return list_of_lang_tuples

class MovieSearchForm(FlaskForm):
    audio = SelectField('Audio', choices=get_tuples(audio_langs), default='English')
    subs = SelectField('Subtitles', choices=get_tuples(sub_langs), default='Spanish')
    year_from = IntegerField('Year From', validators=[NumberRange(min=1900, max=2020)], default=1900)
    year_to = IntegerField('Year To', validators=[NumberRange(min=1900, max=2020)], default=2020)
    filter_movie = BooleanField('Movies', default=True)
    filter_series = BooleanField('Series', default=True)

    # custom validator: at least one of movie/series filters must be checked
    def check_filters():
        pass

class NewWatchlistForm(FlaskForm):
    title = StringField()
    description = StringField()
    is_public = BooleanField()

class LoginForm(FlaskForm):
    username = StringField('User Name')
    password = PasswordField('Password')
    remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    username = StringField('User Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])