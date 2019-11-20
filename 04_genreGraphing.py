# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 06:45:38 2019

@author: night
"""
from collections import defaultdict
import pandas as pd
import networkx as nx
import itertools
import matplotlib.pyplot as plt
import heapq
import pydot
import dill

import graphviz

def save_pkl(df, filename):
    with open('data/'+filename+'.pkl','wb') as fobj:
        dill.dump(df,fobj)
    
def load_pkl(filename):
    with open('data/'+filename+'.pkl','rb') as fobj:
        df = dill.load(fobj)
    return df

def get_genre_list(genre_str):
    import re
    p = re.compile(r"'([A-Za-z &]+)'")
    return p.findall(genre_str)

def create_genre_groups(artist_info):
    genre_ct = defaultdict(int)
    genre_groups = []
    
    for i in range(len(artist_info)):
        genre_list = artist_info.iloc[i]['genres']
#        genre_list = get_genre_list(genre_str)
        genre_groups.append(genre_list)
        
        for genre in genre_list:
            genre_ct[genre] += 1        
    #sort_dict = sorted(genre_ct.items(), key=lambda item: item[1], reverse = True)
    return genre_groups

def create_graph(genre_groups):
    G = nx.MultiGraph()

    for artist_genres in genre_groups:
        G.add_nodes_from(artist_genres)
        for comb in itertools.combinations(artist_genres, 2):
            G.add_edge(comb[0], comb[1])
    #connected = dict(G.degree(weight='weight'))
    
    S = nx.Graph()
    for u,v,data in G.edges(data=True):
        w = data['weight'] if 'weight' in data else 1.0
        if S.has_edge(u,v):
            S[u][v]['weight'] += w
        else:
            S.add_edge(u, v, weight=w)
    return S

def sort_nodes(G):
    degree_dict = {}
    for (a, b) in G.degree():
        degree_dict[a] = b
    heap = [(-value, key) for key,value in degree_dict.items()]
    degree_largest = heapq.nsmallest(100, heap)
    return [key for value, key in degree_largest]

def sort_edges(G):
    weight_dict = {}
    for (a, b, w) in G.edges.data('weight'):
        weight_dict[(a,b)] = w
    heap = [(-value, key) for key,value in weight_dict.items()]
    weight_largest = heapq.nsmallest(100, heap)
    #weight_largest = [(key, -int(value)) for value, key in weight_largest]
    return [key for value, key in weight_largest]

def plot_network_graph(G, top_num, sorted_nodes):
    bignodes=degree_largest[:20]
    G_small = G.subgraph(bignodes)
    pos_small = nx.nx_pydot.graphviz_layout(G_small)
    nx.draw(G_small, pos=pos_small, node_size=50, with_labels=True)
    return G_small

artist_info = load_pkl('artist_df')
genre_groups = create_genre_groups(artist_info)
G = create_graph(genre_groups)
#
nx.readwrite.graphml.write_graphml(G,'data/genregraph.graphml')
#
#weight_largest = sort_edges(S)
#degree_largest = sort_nodes(S)
#
#G_small = plot_network_graph(S, 100, degree_largest)
