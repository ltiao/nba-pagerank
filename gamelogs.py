#!/usr/bin/python

import requests, requests_cache, pprint, yaml

requests_cache.install_cache('gamelog_cache')

payload = {'LeagueID': '00'}    # The field LeagueID must match the regular expression '^\d{2}$'.
r = requests.get('http://stats.nba.com/stats/leaguedashteamstats', params=payload)
print r.text
exit(0)
raw_result = r.json()
pprint.pprint(raw_result)
#print raw_result[u'resultSets'][-1][u'headers']