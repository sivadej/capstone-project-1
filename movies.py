import json

movies_file = open('response.json','r')
resp_json = json.loads(movies_file.read())
movies_file.close()

movies = resp_json.get('ITEMS')