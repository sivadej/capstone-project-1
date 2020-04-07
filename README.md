# What-2-Watch
**What-2-Watch is a language-focused Netflix search tool with the ability to save and share watchlists.**

The inspiration for this project came during the Coronavirus quarantine, where I ended up sheltered with relatives whose first languages were different than mine...

Browsing through Netflix, while you can find foreign-language film categories to get your bilingual fix, there is a lack of language filter options for movies and series. What-2-Watch allows you to pick language and subtitle options for all titles, regardless of the title's primary language. Enjoy movies with friends and family who don't share the same primary language, or use this tool if you're learning a new language.

Search results link titles directly to their Netflix URLs for quick accesss, and will open your Netflix app if you are using the site on a mobile device. Users who register an account have the ability to save movies to watchlists. Users can make their lists private or public. Public watchlists are listed in the Shared Lists page.

Data is pulled from the [Unofficial Netflix Global Search API](https://rapidapi.com/unogs/api/unogsng/details). Results are currently restricted to the US Netflix catalog. 

## Demo
**Live demo deployed to http://what2watch-v01.herokuapp.com/.**

![alt demo](https://github.com/sivadej/what-2-watch/blob/master/w2w_demo-min.gif?raw=true)

#### Built With
- [Flask](https://flask.palletsprojects.com/en/1.1.x/)
- [Postgres](https://www.postgresql.org/)
- [Bootstrap](https://getbootstrap.com/)

##### Tools
- VSCode
- Git
- Insomnia

## Installation
In order to get this project up and running on your local machine, you will need to set up the virtual environment in Python, create the Postgres database, and obtain API credentials from [UNoGS](https://rapidapi.com/unogs/api/unogsng/details).

### Requirements
- Flask 1.0.2
  - Flask-BCrypt 0.7.1
  - Flask-Login 0.5.0
  - Flask-SQLAlchemy 2.3.2
  - Flask-WTF 0.14.2
- SQLAlchemy 1.3
- WTForms 2.2.1

```
> git clone https://github.com/sivadej/what-2-watch.git
> python -m venv .venv
> pip install -r requirements.txt
> source .venv/bin/activate
```

### API & Database Config

Store config variables to ```/config/app_config.py```. If no config folder exists, it will use ```os.environ``` config vars.
- ```DB_URI``` - Postgres DB connection string
- ```API_KEY``` - UNoGS API Key
- ```API_HOST``` - UNoGS Hostname

## Authors
- Sivadej Kitchpanich - [GitHub](https://github.com/sivadej) - [Website](https://sivadej.dev)