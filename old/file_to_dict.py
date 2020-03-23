# file_to_dict for movies
# for development purposes only
# returns a dict of movie data copied from a UNOGS API request


import json

def get_movies_dict():
    movies_file = open('NG_response2.json','r')
    resp_json = json.loads(movies_file.read())
    movies_file.close()
    movies = resp_json
    return movies

def serialize_movies(data):
    return json.loads(data)