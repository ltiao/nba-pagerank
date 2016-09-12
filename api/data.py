import yaml
import requests
import requests_cache
import pandas as pd
import networkx as nx

from fake_useragent import UserAgent
from redis import StrictRedis

from functools import partial, wraps
from operator import attrgetter

from settings import REQUESTS_CACHE_BACKEND, REDIS_HOST, REDIS_PORT


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
def games_df(league_id='00', season='2015-16', season_type='Regular Season',
             team=True, sort_by='date', ascending=True):

    return get_json(url='http://stats.nba.com/stats/LeagueGameLog',
                    params={'LeagueID': league_id,
                            'PlayerOrTeam': 'T' if team else 'P',
                            'Season': season,
                            'SeasonType': season_type,
                            'Sorter': sort_by.upper(),
                            'Direction': 'ASC' if ascending else 'DESC'})


def pivot_games_df(df):

    # primary_columns = [
    #     'TEAM_ID',
    #     'FGM',
    #     'FGA',
    #     'FG3M',
    #     'FG3A',
    #     'FTM',
    #     'FTA',
    #     'OREB',
    #     'DREB',
    #     'AST',
    #     'STL',
    #     'BLK',
    #     'TOV',
    #     'PF',
    #     'PTS',
    # ]
    primary_columns = 'TEAM_ABBREVIATION'

    visitors = df[df['MATCHUP'].str.contains('@')]['TEAM_ABBREVIATION']

    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'], format='%Y-%m-%d')

    df = df.reset_index('GAME_ID')

    pivot_df = df.pivot_table(index=['GAME_ID', 'SEASON_ID', 'GAME_DATE', 'MIN'],
                              columns='WL',
                              values=primary_columns,
                              aggfunc=lambda s: s.iloc[0])
    pivot_df = pivot_df.reset_index(['SEASON_ID', 'GAME_DATE', 'MIN'])
    pivot_df['VISITOR'] = visitors

    return pivot_df


@apply_to_output(to_data_frame,
                 frame_name='TeamYears', frame_index='TEAM_ID')
@apply_to_output(normalize_dict)
def teams_df(league_id='00'):

    # Make Request
    return get_json(url='http://stats.nba.com/stats/commonTeamYears',
                    params={'LeagueID': league_id})


@apply_to_output(to_data_frame,
                 frame_name='TeamInfoCommon', frame_index='TEAM_ABBREVIATION')
@apply_to_output(normalize_dict)
def team_details_df(team_id, league_id='00', season='2015-16',
                    season_type='Regular Season'):

    return get_json(url='http://stats.nba.com/stats/TeamInfoCommon',
                    params={'LeagueID': league_id,
                            'TeamID': team_id,
                            'Season': season,
                            'SeasonType': season_type})


def teams_details_df(league_id='00', season='2015-16',
                     season_type='Regular Season'):

    return pd.concat(map(partial(team_details_df,
                                 league_id=league_id,
                                 season=season,
                                 season_type=season_type),
                         teams_df(league_id=league_id).index))


def g(league_id='00', season='2015-16', season_type='Regular Season',
      create_using=None):

    if create_using is None:
        create_using = nx.MultiDiGraph()

    df = teams_details_df(league_id=league_id, season=season,
                          season_type=season_type)

    G = nx.convert._prep_create_using(create_using)
    G.add_nodes_from(df.to_dict(orient='index').items())

    H = nx.from_pandas_dataframe(df=pivot_games_df(
                                      games_df(league_id=league_id,
                                               season=season,
                                               season_type=season_type)),
                                 # source=('TEAM_ID', 'L'),
                                 # target=('TEAM_ID', 'W'),
                                 source='L',
                                 target='W',
                                 edge_attr=True,
                                 create_using=nx.MultiDiGraph())

    return nx.compose(G=G, H=H, name='win_loss_network')
