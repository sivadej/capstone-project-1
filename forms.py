from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, BooleanField
from wtforms.validators import InputRequired, Length, Email, NumberRange

language_list = ['English','Spanish','Cantonese','Brazilian','Tagalog','French','German','Mandarin','Arabic','Korean','Slovak','Thai','Chinese','Turkish','Vietnamese']
#language_list = language_list.sort()
def get_tuples(langs):
    list_of_lang_tuples=[]
    for lang in langs:
        list_of_lang_tuples.append((lang,lang))
    return list_of_lang_tuples
lang_tuples = get_tuples(language_list)

class MovieSearchForm(FlaskForm):
    audio = SelectField('Audio', choices=lang_tuples)
    subs = SelectField('Subtitles', choices=lang_tuples)
    #year = IntegerField('Year Range', validators=[NumberRange(min=1900, max=2020)])

class NewWatchlistForm(FlaskForm):
    title = StringField()
    description = StringField()
    is_public = BooleanField()







