from api_config import API2_KEY, API2_HOST
from html import unescape

file_name = 'NG_response2.json'

#query = '' #leave blank
#syear = 1950 #start year
#eyear = 2020 #end year
#snfrate = 0 #netflix rating min
#enfrate = 5 #netflix rating max
#simdbrate = 0 #imdb rating min
#eimdbrate = 10 #imdb rating max
##genreid = 0
##vtype = 'Movie' #Any, Movie, Series
##audio = 'English' #language audio
##subtitle = 'Thai' #language subtitle
#imdbvotes = '' #IMDB Votes: use gt[num] for greater than and lt[num] for less than
#downloadable = '' #optional. Yes, No, blank
#andor = 'and' # and, or
#clist = 78 #country ids
#sortby = 'Relevance' # Sort Results by: Relevance, Date, Rating, Title, VideoType, FilmYear, Runtime
#page = 1 # page number. 100 per page

#my_query = f'{query}-!{syear},{eyear}-!{snfrate},{enfrate}-!{simdbrate},{eimdbrate}-!{genreid}-!{vtype}-!{audio}-!{subtitle}-!{imdbvotes}-!{downloadable}&t=ns&cl={clist}&st=adv&ob={sortby}&p={page}&sa={andor}'
end_year = 2020
start_year = 1950
limit = 100
offset = 0
videotype = None #movie or series
audio = 'thai'
subtitle = 'english'

qstring = f'end_year={end_year}&audiosubtitle_andor=and&start_year={start_year}&countrylist=78&limit={limit}&offset={offset}&audio={audio}&subtitle={subtitle}'

import requests

url = f'https://unogsng.p.rapidapi.com/search?{qstring}'

#querystring = {"q":"-!1900,2018-!0,5-!0,10-!0-!Any-!Any-!Any-!gt100-!{downloadable}","t":"ns","cl":"all","st":"adv","ob":"Relevance","p":"1","sa":"and"}

#f'{query}-!{syear},{eyear}-!{snfrate},{enfrate}-!{simdbrate},{eimdbrate}-!{genreid}-!{vtype}-!{audio}-!{subtitle}-!{imdbvotes}-!{downloadable}&t=ns&cl={clist}&st=adv&ob={sortby}&p={page}&sa={andor}'


headers = {
    'x-rapidapi-host': API2_HOST,
    'x-rapidapi-key': API2_KEY
    }

response = requests.request("GET", url, headers=headers)

#print(response.json())
#print(response.text)
f = open(file_name,'w')
f.write(unescape(response.text))
f.close()
print(url)
print(f'results written to {file_name}')
