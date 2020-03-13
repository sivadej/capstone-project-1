from api_config import API_KEY, API_HOST

file_name = 'myresponse.json'

query = '' #leave blank
syear = 1950 #start year
eyear = 2020 #end year
snfrate = 0 #netflix rating min
enfrate = 5 #netflix rating max
simdbrate = 0 #imdb rating min
eimdbrate = 10 #imdb rating max
genreid = 0
vtype = 'Movie' #Any, Movie, Series
audio = 'English' #language audio
subtitle = 'Thai' #language subtitle
imdbvotes = '' #IMDB Votes: use gt[num] for greater than and lt[num] for less than
downloadable = '' #optional. Yes, No, blank
andor = 'and' # and, or
clist = 78 #country ids
sortby = 'Relevance' # Sort Results by: Relevance, Date, Rating, Title, VideoType, FilmYear, Runtime
page = 1 # page number. 100 per page

my_query = f'{query}-!{syear},{eyear}-!{snfrate},{enfrate}-!{simdbrate},{eimdbrate}-!{genreid}-!{vtype}-!{audio}-!{subtitle}-!{imdbvotes}-!{downloadable}&t=ns&cl={clist}&st=adv&ob={sortby}&p={page}&sa={andor}'

import requests

url = f'https://unogs-unogs-v1.p.rapidapi.com/aaapi.cgi?q={my_query}'

#querystring = {"q":"-!1900,2018-!0,5-!0,10-!0-!Any-!Any-!Any-!gt100-!{downloadable}","t":"ns","cl":"all","st":"adv","ob":"Relevance","p":"1","sa":"and"}

#f'{query}-!{syear},{eyear}-!{snfrate},{enfrate}-!{simdbrate},{eimdbrate}-!{genreid}-!{vtype}-!{audio}-!{subtitle}-!{imdbvotes}-!{downloadable}&t=ns&cl={clist}&st=adv&ob={sortby}&p={page}&sa={andor}'

headers = {
    'x-rapidapi-host': API_HOST,
    'x-rapidapi-key': API_KEY
    }

response = requests.request("GET", url, headers=headers)

#print(response.json())
#print(response.text)
f = open(file_name,'w')
f.write(response.text)
f.close()

print(f'results written to {file_name}')