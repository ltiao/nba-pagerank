from fake_useragent import UserAgent
from redis import StrictRedis

from functools import partial, wraps
from operator import attrgetter

from settings import REQUESTS_CACHE_BACKEND, REDIS_HOST, REDIS_PORT

import yaml
import requests
import requests_cache
import pandas as pd

requests_cache.install_cache(
    'nba-rank',
    expire_after=24*60*60,
    backend=REQUESTS_CACHE_BACKEND,
    connection=StrictRedis(
        host=REDIS_HOST,
        port=REDIS_PORT
    )
)


def apply_to_output(callback, *cb_args, **cb_kwargs):

    def decorator(func):

        @wraps(func)
        def new_func(*args, **kwargs):
            return callback(func(*args, **kwargs), *cb_args, **cb_kwargs)

        return new_func

    return decorator


def get_json(url, *args, **kwargs):
    r = requests.get(url=url, *args, **kwargs)
    r.raise_for_status()
    return r.json()


def nested_dict_from_lst(lst, key):
    return {d.pop(key): d for d in lst}


def normalize_dict(dct, frame_name_key='name', frames_key='resultSets',
                   frames_default=[]):
    return nested_dict_from_lst(dct.get(frames_key, frames_default),
                                key=frame_name_key)


def to_data_frame(frames_dict, frame_name, frame_index=None,
                  frame_data_key='rowSet', frame_columns_key='headers'):
    return pd.DataFrame.from_records(
               data=frames_dict[frame_name][frame_data_key],
               columns=frames_dict[frame_name][frame_columns_key],
               index=frame_index).dropna()


ua = UserAgent()
get_json = partial(get_json, headers={'User-Agent': ua.google})


@apply_to_output(to_data_frame,
                 frame_name='LeagueGameLog', frame_index='GAME_ID')
@apply_to_output(normalize_dict)
def games(league_id='00', season='2015-16', season_type='Regular Season',
          team=True, sort_by='date', ascending=True):

    return get_json(url='http://stats.nba.com/stats/LeagueGameLog',
                    params={'LeagueID': league_id,
                            'PlayerOrTeam': 'T' if team else 'P',
                            'Season': season,
                            'SeasonType': season_type,
                            'Sorter': sort_by.upper(),
                            'Direction': 'ASC' if ascending else 'DESC'})


@apply_to_output(to_data_frame, frame_name='TeamYears', frame_index='TEAM_ID')
@apply_to_output(normalize_dict)
def teams(league_id='00'):

    # Make Request
    return get_json(url='http://stats.nba.com/stats/commonTeamYears',
                    params={'LeagueID': league_id})


@apply_to_output(to_data_frame,
                 frame_name='TeamInfoCommon', frame_index='TEAM_ID')
@apply_to_output(normalize_dict)
def team_details(team_id, league_id='00', season='2015-16',
                 season_type='Regular Season'):

    return get_json(url='http://stats.nba.com/stats/TeamInfoCommon',
                    params={'LeagueID': league_id,
                            'TeamID': team_id,
                            'Season': season,
                            'SeasonType': season_type})


def teams_details(league_id='00', season='2015-16',
                  season_type='Regular Season'):

    return pd.concat(map(partial(team_details,
                                 league_id=league_id,
                                 season=season,
                                 season_type=season_type),
                         teams(league_id=league_id).index))
