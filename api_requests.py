from api_config import API2_KEY, API2_HOST
import requests

def get_data():
    end_year = 2020
    start_year = 1950
    limit = 100
    offset = 0
    videotype = None #movie or series
    audio = 'thai'
    subtitle = 'english'

    qstring = f'end_year={end_year}&audiosubtitle_andor=and&start_year={start_year}&countrylist=78&limit={limit}&offset={offset}&audio={audio}&subtitle={subtitle}'

    url = f'https://unogsng.p.rapidapi.com/search?{qstring}'

    headers = {
        'x-rapidapi-host': API2_HOST,
        'x-rapidapi-key': API2_KEY
        }

    try:
        response = requests.request("GET", url, headers=headers)
    except:
        return('api request err')

    return(response.text)