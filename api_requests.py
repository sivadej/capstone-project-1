from api_config import API2_KEY, API2_HOST
import requests
from html import unescape
from file_to_dict import get_movies_dict, serialize_movies
from models import db, Movie

def single_movie_to_db(mov):
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
        print('movie saved to db.')
    except:
        #print('movie not added to dbsession')
        db.session.rollback()
        pass


# pass in list of movie dicts
# add to movies table 
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
            print('movie saved to db.')
        except:
            #print('movie not added to dbsession')
            db.session.rollback()
            pass
    print('all movies scanned')
    
    #db.session.commit()
    #print('saved movie to db')
    #import pdb;pdb.set_trace()
    #pass

def get_data(lang1, lang2):
    end_year = 2020
    start_year = 1950
    limit = 25
    offset = 0
    videotype = None #movie or series
    audio = lang1
    subtitle = lang2

    qstring = f'end_year={end_year}&audiosubtitle_andor=and&start_year={start_year}&countrylist=78&limit={limit}&offset={offset}&audio={audio}&subtitle={subtitle}'

    url = f'https://unogsng.p.rapidapi.com/search?{qstring}'

    headers = {
        'x-rapidapi-host': API2_HOST,
        'x-rapidapi-key': API2_KEY
        }

    try:
        response = requests.request("GET", url, headers=headers)
    except:
        return('api connection err')
    
    return(unescape(response.text))