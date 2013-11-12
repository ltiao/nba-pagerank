#!/usr/bin/python

import requests, requests_cache, pprint, yaml

requests_cache.install_cache('gamelog_cache')

with open("teams_config.yaml", 'r') as infile:
    payload = yaml.load(infile)

r = requests.get('http://stats.nba.com/stats/leaguedashteamstats', params=payload)
raw_result = r.json()
headers = [h.lower() for h in raw_result[u'resultSets'][-1][u'headers'][1:]] # omit the 'TEAM_ID' header and convert everything to lowercase

team_stats = {}

for row in raw_result[u'resultSets'][-1][u'rowSet']:
    team_id, row_data = row[0], row[1:] 
    team_stats[team_id] = dict(zip(headers, row_data))

pprint.pprint(team_stats)