#!/usr/bin/python

import requests, requests_cache, pprint, yaml

requests_cache.install_cache('gamelog_cache')

with open("teams_config.yaml", 'r') as infile:
    payload = yaml.load(infile)

r = requests.get('http://stats.nba.com/stats/leaguedashteamstats', params=payload)
raw_result = r.json()
#print raw_result
#pprint.pprint(raw_result)
print dict(row[:2] for row in raw_result[u'resultSets'][-1][u'rowSet'])