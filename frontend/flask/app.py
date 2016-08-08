from flask import Flask, jsonify, request
from redis import StrictRedis

from settings import REDIS_HOST, REDIS_PORT

import yaml
import requests
import requests_cache
import pandas as pd

requests_cache.install_cache(
    'nba-rank',
    expire_after=24*60*60,
    backend='redis',
    connection=StrictRedis(
        host=REDIS_HOST,
        port=REDIS_PORT
    )
)

app = Flask(__name__)


def list_of_dicts_to_nested_dict(lst, key):
    return {d.pop(key): d for d in lst}


def teams():

    r = requests.get(url='http://stats.nba.com/stats/commonTeamYears',
                     params={'LeagueID': '00'})
    r.raise_for_status()
    print(r.from_cache)
    result_sets = list_of_dicts_to_nested_dict(r.json().get('resultSets', []),
                                               key='name')

    df = pd.DataFrame(
            data=result_sets['TeamYears']['rowSet'],
            columns=result_sets['TeamYears']['headers']
         ).dropna().set_index('TEAM_ID')

    return df


@app.route('/')
def greeting():
    print(teams())
    return jsonify([1, 4])

if __name__ == '__main__':
    # Start server
    app.run(port=8080, debug=True)
