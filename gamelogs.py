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

def all_team_stats(**kwargs):
    with open("teams_config.yaml", 'r') as infile:
        payload = yaml.load(infile)
    payload.update(kwargs) # Update default parameters with kwargs
    r = requests.get('http://stats.nba.com/stats/leaguedashteamstats', params=payload)
    r.raise_for_status()
    return preprocess(r.json())  
    
def team_gamelog(team_id, season, season_type='Regular Season'):
    # # TODO: Use **kwargs here
    payload = {
        'TeamID': team_id,
        'Season': season,
        'SeasonType': season_type,
    }
    r = requests.get('http://stats.nba.com/stats/teamgamelog', params=payload)
    r.raise_for_status()
    return preprocess(r.json(), identifier=1)

def team_detail(team_id):
    # [u'TeamDetails'][0][u'Details'][0]
    r = requests.get('http://stats.nba.com/feeds/teams/profile/{team_id}_TeamProfile.js'.format(team_id=team_id))
    r.raise_for_status()
    return r.json()[u'TeamDetails'][0][u'Details'][0]

import networkx as nx
G = nx.MultiDiGraph()

games = {}
teams = all_team_stats()
for team_id in teams:
    detail = team_detail(team_id)
    G.add_node(team_id, abbr=detail[u'Abbreviation'], city=detail[u'City'], nickname=detail[u'Nickname'])
    team_games = team_gamelog(team_id, '2013-14')
    for game_id in team_games:
        won = int(team_games[game_id][u'wl'] == 'W')
        if not game_id in games: games[game_id] = []
        team_games[game_id][u'team_id'] = team_id
        games[game_id].insert(won, team_games[game_id])
        if len(games[game_id]) == 2: 
            a = tuple(t[u'team_id'] for t in games[game_id])
            G.add_edge(*a, key=game_id, weight=games[game_id][1][u'pts']-games[game_id][0][u'pts'])

#print G[1610612737][1610612752]

M = nx.google_matrix(G)
print M

exit(0)

gamelog = {}
teams = all_team_stats()
for team_id in teams:
    print 'getting games for {team}'.format(team=teams[team_id]['team_name'])
    team_games = team_gamelog(team_id, '2013-14')
    for game_id in team_games:
        if not game_id in gamelog:
            gamelog[game_id] = {}
        gamelog[game_id][team_id] = team_games[game_id]

pprint.pprint(gamelog)
print len(gamelog.keys())