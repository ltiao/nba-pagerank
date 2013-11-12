#!/usr/bin/python

import requests, requests_cache, pprint, yaml

requests_cache.install_cache('gamelog_cache')

def all_team_stats():
    with open("teams_config.yaml", 'r') as infile:
        payload = yaml.load(infile)
    # TODO: Use **kwargs to override dict values
    r = requests.get('http://stats.nba.com/stats/leaguedashteamstats', params=payload)
    raw_result = r.json()
    headers = [h.lower() for h in raw_result[u'resultSets'][-1][u'headers'][1:]] # omit the 'TEAM_ID' header and convert everything to lowercase
    return dict((row[0], dict(zip(headers, row[1:]))) for row in raw_result[u'resultSets'][-1][u'rowSet'])
    
def team_gamelog(team_id, season, season_type):
    # TODO: Use **kwargs here
    payload = {
        'TeamID': team_id,
        'Season': season,
        'SeasonType': season_type,
    }
    r = requests.get('http://stats.nba.com/stats/teamgamelog', params=payload)
    raw_result = r.json()
    
team_stats = all_team_stats()
print team_stats