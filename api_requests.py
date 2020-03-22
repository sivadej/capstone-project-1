from app_config import API_KEY, API_HOST
import requests
from html import unescape
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

def get_data(audio, subs, start_year=1900, end_year=2020, offset=0, filter_movie=True, filter_series=True):
    end_year = end_year
    start_year = start_year
    limit = 12
    offset = offset
    audio = audio
    subtitle = subs

    # handle movie/series filter
    if filter_movie is True and filter_series is True:
        vtype = ''
    elif filter_movie is True and filter_series is False:
        vtype = '&type=movie'
    elif filter_movie is False and filter_series is True:
        vtype = '&type=series'
    else:
        raise

    # build API request args
    url = f'https://unogsng.p.rapidapi.com/search?end_year={end_year}&audiosubtitle_andor=and&start_year={start_year}&countrylist=78&limit={limit}&offset={offset}&audio={audio}&subtitle={subtitle}{vtype}'
    headers = {
        'x-rapidapi-host': API_HOST,
        'x-rapidapi-key': API_KEY,
        }

    try:
        response = requests.request("GET", url, headers=headers)
    except:
        return('api connection err')
    
    return(unescape(response.text))

def get_data_next_page():
    pass