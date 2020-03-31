from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, BooleanField
from wtforms.validators import InputRequired, Length, Email, NumberRange

audio_langs = ['English','Spanish','Cantonese','Tagalog','French','German','Mandarin','Arabic','Korean','Thai','Turkish','Vietnamese','Russian','Portuguese','Polish']
sub_langs = ['English','Spanish','Tagalog','French','German','Arabic','Korean','Thai','Chinese','Turkish','Vietnamese','Russian','Portuguese','Polish']

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
    title = StringField('Watchlist Title', validators=[InputRequired()])
    description = StringField('Description')
    is_shared = BooleanField('Make Public')

class LoginForm(FlaskForm):
    username = StringField('User Name', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    username = StringField('User Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])

class EditUserForm(FlaskForm):
    username = StringField('User Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    #password = PasswordField('Password', validators=[InputRequired()])

class EditWatchlistForm(FlaskForm):
    title = StringField('Watchlist Title', validators=[InputRequired()])
    description = StringField('Description')
    is_shared = BooleanField('Make Public')

class PickWatchlistForMovieForm(FlaskForm):
    watchlist = SelectField('Watchlist', coerce=int)