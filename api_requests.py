from app_config import API_KEY, API_HOST
import requests
from html import unescape
from file_to_dict import get_movies_dict, serialize_movies
from models import db, Movie

def save_to_db(movies):
    for mov in movies:
        new_movie = Movie(
            video_type = mov['vtype'],
            netflix_id = mov['nfid'],
            title = mov['title'],
            image_url = mov['img'],
            synopsis = mov['synopsis'],
            year = mov['year'],
            imdb_id = None if mov['imdbid'] == 'notfound' else mov['imdbid'],
            unogs_id = mov['id'],
        )
        try:
            db.session.add(new_movie)
            db.session.commit()
        except:
            db.session.rollback()

def get_data(audio, subs):
    end_year = 2020
    start_year = 1950
    limit = 12
    offset = 0
    videotype = None #movie or series
    audio = audio
    subtitle = subs

    url = f'https://unogsng.p.rapidapi.com/search?end_year={end_year}&audiosubtitle_andor=and&start_year={start_year}&countrylist=78&limit={limit}&offset={offset}&audio={audio}&subtitle={subtitle}'

    headers = {
        'x-rapidapi-host': API_HOST,
        'x-rapidapi-key': API_KEY
        }

    try:
        response = requests.request("GET", url, headers=headers)
    except:
        return('api connection err')
    
    return(unescape(response.text))