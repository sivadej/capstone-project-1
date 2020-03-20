# file_to_dict for movies
import json

def get_movies_dict():
    movies_file = open('NG_response1.json','r')
    resp_json = json.loads(movies_file.read())
    movies_file.close()
    movies = resp_json
    return movies