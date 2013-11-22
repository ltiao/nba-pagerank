#!/usr/bin/python

import networkx as nx
import StringIO
from nba_pagerank.datasets.data import graph, team_detail
from networkx.readwrite import json_graph
import pprint


G = graph('2013-14', include=['MIA', 'ATL', 'CHA', 'ORL', 'WAS', 'IND', 'CHI', 'DET', 'CLE', 'MIL', 'TOR', 'PHI', 'BOS', 'NYK', 'BKN'])

data = json_graph.node_link_data(G)
pprint.pprint(data)

exit(0)

import matplotlib.pyplot as plt

M = nx.pagerank_numpy(G, alpha=0.9)

labels = dict((node, G.node[node]['abbr']) for node in G.nodes())
nodelist = sorted(labels, key=lambda k: labels[k])
node_size = [M[node]*100*300 for node in nodelist]

nx.draw_circle(G, labels=labels, nodelist=nodelist, node_size=node_size, alpha=0.9)
plt.savefig("path.pdf", format='pdf')

exit(0)

M = nx.pagerank_numpy(G, alpha=0.9)
for team in sorted(M.keys(), key=lambda k: M[k], reverse=True):
    print team, team_detail(team)[u'Abbreviation'], G.in_degree(team), G.out_degree(team), round(G.in_degree(team)/float(G.out_degree(team)+G.in_degree(team)), 3), M[team]