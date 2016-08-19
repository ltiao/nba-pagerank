from flask import Flask, Blueprint, jsonify, request
from redis import StrictRedis

from settings import REQUESTS_CACHE_BACKEND, REDIS_HOST, REDIS_PORT
from fake_useragent import UserAgent

import yaml
import requests
import requests_cache
import pandas as pd

ua = UserAgent()

requests_cache.install_cache(
    'nba-rank',
    expire_after=24*60*60,
    backend=REQUESTS_CACHE_BACKEND,
    connection=StrictRedis(
        host=REDIS_HOST,
        port=REDIS_PORT
    )
)

api = Blueprint('something', __name__, template_folder='templates')


def pivot_dict(lst, key):
    return {d.pop(key): d for d in lst}


def gamelog():

    r = requests.get(url='http://stats.nba.com/stats/leaguegamelog',
                     headers={'User-Agent': ua.google},
                     params={
                         "LeagueID": "00",
                         "PlayerOrTeam": "T",
                         "Season": "2015-16",
                         "SeasonType": "Regular Season",
                         "Sorter": "DATE",
                         "Direction": "ASC"})
    r.raise_for_status()

    app.logger.info('Using cached data: {}'.format(r.from_cache))

    result_sets = pivot_dict(r.json().get('resultSets', []), key='name')

    df = pd.DataFrame.from_records(data=result_sets['LeagueGameLog']['rowSet'],
                                   columns=result_sets['LeagueGameLog']['headers'],
                                   index=['SEASON_ID', 'GAME_ID', 'TEAM_ID']).dropna()

    app.logger.info('Resulting DataFrame:\n{}'.format(df))

    return df


def teams():

    r = requests.get(url='http://stats.nba.com/stats/commonTeamYears',
                     headers={'User-Agent': ua.google},
                     params={'LeagueID': '00'})
    r.raise_for_status()

    app.logger.info('Using cached data: {}'.format(r.from_cache))

    result_sets = pivot_dict(r.json().get('resultSets', []), key='name')

    df = pd.DataFrame.from_records(data=result_sets['TeamYears']['rowSet'],
                                   columns=result_sets['TeamYears']['headers'],
                                   index=['TEAM_ID']).dropna()

    app.logger.info('Resulting DataFrame:\n{}'.format(df))

    return df


@api.route('/')
def greeting():
    games_df = gamelog()
    return jsonify(games_df.index.values.tolist())

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    # Start server
    app.run(port=8080, debug=True)
