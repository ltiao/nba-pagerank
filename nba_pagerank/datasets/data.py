#!/usr/bin/python

import datetime, os, redis, requests, requests_cache, pprint, yaml
import networkx as nx

if 'REDISTOGO_URL' in os.environ:
    redis_url = os.environ.get('REDISTOGO_URL', 'redis://redistogo:d7a9d2fec3de08de3aa9a562cb34ad1e@beardfish.redistogo.com:10002/')
    redis = redis.from_url(redis_url)
    requests_cache.install_cache('gamelog_cache', backend='redis', expire_after=24*60*60, connection=redis) # 1 day
else:
# requests_cache.install_cache('gamelog_cache', backend='redis', expire_after=24*60*60, connection=redis) # 1 day
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

def gamelog(season, season_type='Regular Season'):
    gamelog = {}
    teams = all_team_stats()
    for team_id in teams:
        print 'getting games for {team}'.format(team=teams[team_id]['team_name'])
        team_games = team_gamelog(team_id, season, season_type)
        for game_id in team_games:
            if not game_id in gamelog:
                gamelog[game_id] = {}
            gamelog[game_id][team_id] = team_games[game_id]
    return gamelog
    
def team_detail(team_id):
    # [u'TeamDetails'][0][u'Details'][0]
    r = requests.get('http://stats.nba.com/feeds/teams/profile/{team_id}_TeamProfile.js'.format(team_id=team_id))
    r.raise_for_status()
    return r.json()[u'TeamDetails'][0][u'Details'][0]

def graph(season='2013-14', include=None, exclude=None, date_range=None):
    G = nx.MultiDiGraph()
    games = {}
    teams = all_team_stats(Season=season)
    for team_id in teams:
        detail = team_detail(team_id)
        if include and not detail[u'Abbreviation'] in include: continue
        if exclude and detail[u'Abbreviation'] in exclude: continue
        G.add_node(team_id, abbr=detail[u'Abbreviation'], city=detail[u'City'], nickname=detail[u'Nickname'])
        team_games = team_gamelog(team_id, season)
        for game_id in team_games:
            if not game_id in games: games[game_id] = {}
            if team_games[game_id].pop(u'wl') == 'W':
                games[game_id][u'winner'] = team_id
            else:
                games[game_id][u'loser'] = team_id
            matchup = team_games[game_id].pop(u'matchup')
            if '@' in matchup: 
                games[game_id][u'away'] = team_id
            else: 
                games[game_id][u'home'] = team_id
            games[game_id][u'date'] = datetime.datetime.strptime(team_games[game_id].pop(u'game_date'), '%b %d, %Y').date()
            games[game_id][u'minutes'] = team_games[game_id].pop(u'min')
            games[game_id][team_id] = team_games[game_id]
            
            if 'winner' in games[game_id] and 'loser' in games[game_id]:
                pts_differential = games[game_id][games[game_id]['winner']][u'pts'] - games[game_id][games[game_id]['loser']][u'pts']
                G.add_edge(games[game_id]['loser'], games[game_id]['winner'], game_id, date=games[game_id][u'date'], pts_diff=pts_differential)#, games[game_id])
    return G

# M = nx.pagerank_numpy(G, alpha=0.9)
# for team in sorted(M.keys(), key=lambda k: M[k], reverse=True):
#     print team, team_detail(team)[u'Abbreviation'], G.in_degree(team), G.out_degree(team), round(G.in_degree(team)/float(G.out_degree(team)+G.in_degree(team)), 3), M[team]