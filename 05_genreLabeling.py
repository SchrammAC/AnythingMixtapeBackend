# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 11:42:18 2019

@author: night
"""
import pandas as pd
import dill

def get_genre_list(genre_str):
    import re
    p = re.compile(r"'([A-Za-z &]+)'")
    return p.findall(genre_str)

def make_df(overall_list, genre_list):
    genre_dict = {}
#    genre_dict['artist'] = overall_list[0]
    for i in range(len(genre_list)):
        genre_dict[genre_list[i]] = overall_list[i]
    return pd.DataFrame(genre_dict)

def combine_df(artist_df, genre_df):
    return pd.concat([artist_df.loc[:,['artist','artist_id','popularity']], genre_df], axis=1)

def genre_from_mod(genre, graph_analysis):
    mod_class = int(graph_analysis[graph_analysis['Id']==genre].modularity_class)
    if mod_class in [2]:
        return [0, 1, 0] #hiphop
    if mod_class in [0,3,4]:
        return [1, 0, 0] #rock
    if mod_class in [5]:
        return [0, 0, 1] #country
    else:
        return [0, 0, 0]

def genre_transformer(artist_df,graph_analysis):
    genre_cats = ['rock', 'hiphop', 'country']
    overall_list = [[], [], []]
    genre_list_df = artist_df['genres']
    modded_genre_list = list(graph_analysis.Id)
    for i in range(len(genre_list_df)):
        genre_list = genre_list_df[i] 
        if genre_list and (genre_list[0] in modded_genre_list):
            category = genre_from_mod(genre_list[0], graph_analysis)
        else:
            category = [0, 0, 0]
        for i in range(len(category)):
            overall_list[i].append(category[i])
            
    genre_df = make_df(overall_list, genre_cats)
    
    total_df = combine_df(artist_df, genre_df)
    return total_df

def save_pkl(df, filename):
    with open('data/'+filename+'.pkl','wb') as fobj:
        dill.dump(df,fobj)
    
def load_pkl(filename):
    with open('data/'+filename+'.pkl','rb') as fobj:
        df = dill.load(fobj)
    return df
    
artist_df = load_pkl('artist_df')



graph_analysis = pd.read_csv('data/190808_GraphData.csv')

total_df = genre_transformer(artist_df,graph_analysis)

filename = 'artist_genre_df'
save_pkl(total_df, filename)


