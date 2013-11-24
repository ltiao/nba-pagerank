#!/usr/bin/python

import numpy as np
import networkx as nx
import StringIO
from nba_pagerank.datasets.data import graph, team_detail
from networkx.readwrite import json_graph
import pprint

    # ['GSW', 'LAC', 'PHX', 'LAL', 'SAC', 'POR', 'OKC', 'MIN', 'DEN', 'UTA']
atlantic = ['NYK', 'BKN', 'BOS', 'PHI', 'TOR']
central = ['IND', 'CHI', 'MIL', 'DET', 'CLE']
southeast = ['MIA', 'ATL', 'WAS', 'CHA', 'ORL']
northwest = ['OKC', 'DEN', 'UTA', 'POR', 'MIN']
pacific = ['GSW', 'LAC', 'PHX', 'LAL', 'SAC']
southwest = ['SAS', 'MEM', 'HOU', 'DAL', 'NOH']

teams = []
teams.extend(atlantic)
teams.extend(central)
teams.extend(southeast)
teams.extend(northwest)
teams.extend(pacific)
teams.extend(southwest) 

import random

A = ['SAS', 'CHA']

A.extend(random.sample(teams, 4))

G = graph('2013-14')#random.sample(teams, 6))

# M = nx.to_numpy_matrix(G)#, nodelist=sorted(G.nodes(), key=lambda k: G.node[k]['abbr']))
# 
# print [G.node[k]['abbr'] for k in G.nodes()]#sorted(G.nodes(), key=lambda k: G.node[k]['abbr'])]
# print M
# M = nx.pagerank_numpy(G)
# for team in sorted(M.keys(), key=lambda k: M[k], reverse=True):
#     print team, team_detail(team)[u'Abbreviation'], G.in_degree(team), G.out_degree(team), round(G.in_degree(team)/float(G.out_degree(team)+G.in_degree(team)), 3), M[team]
# 
# print 'Start'
# 
# print [G.node[k]['abbr'] for k in G.nodes()]
# print nx.to_numpy_matrix(G)#, nodelist=sorted(G.nodes(), key=lambda k: G.node[k]['abbr']))
# print nx.google_matrix(G)
# M = nx.pagerank_numpy(G)
# for team in M:
#     print team, team_detail(team)[u'Abbreviation'], G.in_degree(team), G.out_degree(team), round(G.in_degree(team)/float(G.out_degree(team)+G.in_degree(team)), 3), M[team]
# 
# exit(0)

import matplotlib.pyplot as plt

M = nx.pagerank_numpy(G)

labels = dict((node, G.node[node]['abbr']) for node in G.nodes())
nodelist = sorted(labels, key=lambda k: labels[k])
node_size = [M[node]*100*600 for node in nodelist]

nx.draw_graphviz(G, labels=labels, nodelist=nodelist, node_size=node_size, alpha=0.9)
plt.savefig("path.pdf", format='pdf')

for team in sorted(M.keys(), key=lambda k: M[k], reverse=True):
    print team, team_detail(team)[u'Abbreviation'], G.in_degree(team), G.out_degree(team), round(G.in_degree(team)/float(G.out_degree(team)+G.in_degree(team)), 3), M[team]
   
print '###'

print G.in_edges(1610612745)

print """
\\begin{tabular}{l*{3}{c}r}
Team    & W     & L	    & Ratio & Pagerank \\\\
\\hline
"""
for team, junk in sorted(G.in_edges(1610612740), key=lambda k: M[k[0]], reverse=True):
    print '{team}  & {w}   & {l}   & {pct:.3f} & {pagerank:.3f} \\\\'.format(
        team = team_detail(team)[u'Abbreviation'], 
        w = G.in_degree(team), 
        l = G.out_degree(team), 
        pct = round(G.in_degree(team)/float(G.out_degree(team)+G.in_degree(team)), 3), 
        pagerank = round(M[team],3)
    )	   
print '\\end{tabular}'