#!/usr/bin/python

import requests, requests_cache, pprint, yaml

requests_cache.install_cache('gamelog_cache', expire_after=24*60*60) # 1 day

def preprocess(raw_dict, identifier=0):
    """
    Assume anything before identifier can be omitted and everything 
    immediately after identifier is important
    """
    headers = [h.lower() for h in raw_dict[u'resultSets'][-1][u'headers'][identifier+1:]]
    return dict((row[identifier], dict(zip(headers, row[identifier+1:]))) for row in raw_dict[u'resultSets'][-1][u'rowSet'])

def all_team_stats():
    with open("teams_config.yaml", 'r') as infile:
        payload = yaml.load(infile)
    # TODO: Use **kwargs to override dict values
    r = requests.get('http://stats.nba.com/stats/leaguedashteamstats', params=payload)
    return preprocess(r.json())
    
def team_gamelog(team_id, season, season_type='Regular Season'):
    # TODO: Use **kwargs here
    payload = {
        'TeamID': team_id,
        'Season': season,
        'SeasonType': season_type,
    }
    r = requests.get('http://stats.nba.com/stats/teamgamelog', params=payload)
    return preprocess(r.json(), identifier=1)
    
gamelog = {}
teams = all_team_stats()
for team_id in teams:
    print 'getting games for {team}'.format(team=teams[team_id]['team_name'])
    team_games = team_gamelog(team_id, '2010-11')
    for game_id in team_games:
        if not game_id in gamelog:
            gamelog[game_id] = {}
        gamelog[game_id][team_id] = team_games[game_id]

pprint.pprint(gamelog)
print len(gamelog.keys())