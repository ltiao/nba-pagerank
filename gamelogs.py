#!/usr/bin/python

import networkx as nx
from nba_pagerank.datasets.data import graph, team_detail

G = graph('2013-14')

M = nx.pagerank_numpy(G, alpha=0.9)
for team in sorted(M.keys(), key=lambda k: M[k], reverse=True):
    print team, team_detail(team)[u'Abbreviation'], G.in_degree(team), G.out_degree(team), round(G.in_degree(team)/float(G.out_degree(team)+G.in_degree(team)), 3), M[team]