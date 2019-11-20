# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 10:59:27 2019

@author: night
"""
import dill
import pandas as pd

def save_pkl(df, filename):
    with open('data/'+filename+'.pkl','wb') as fobj:
        dill.dump(df,fobj)
    
def load_pkl(filename):
    with open('data/'+filename+'.pkl','rb') as fobj:
        df = dill.load(fobj)
    return df

def join_track_labels(track_df, artist_df, lyric_df):
    track_wlyrics = track_df.join(lyric_df.lyrics, on='orig_index')
    track_wlyrics_labels = track_wlyrics.join(artist_df[['rock','hiphop','country']], on=['artist_id'], how='inner')
    return track_wlyrics_labels

def get_genre_df(df, label):
    genre_ser = df.loc[df[label]==1][['lyrics', 'track_id']]
    genre_ser.drop_duplicates(inplace=True)
    genre_ser = genre_ser.reset_index()
    label_list = pd.Series([label for row in genre_ser.lyrics], name='genre')
    genre_df = pd.concat([genre_ser, label_list], axis=1, ignore_index=True)
    genre_df = genre_df.rename(columns={0:'orig_index', 1:'lyrics', 2:'track_id', 3:'genre'})
    return genre_df

def get_labeled_df(df, labels):
    labeled_df = pd.DataFrame(columns = ['orig_index', 'lyrics', 'genre', 'track_id'])
    for label in labels:
        genre_df = get_genre_df(df, label)
        labeled_df = labeled_df.append(genre_df, ignore_index=True)
    return labeled_df
    
artist_df = load_pkl('artist_genre_df').set_index('artist_id')
artist_idlist = list(artist_df.index)

track_df = load_pkl('track_df')

filtered_track_df = track_df[track_df.artist_id.isin(artist_idlist)]
lyric_df = load_pkl('track_lyrics')

total_df = join_track_labels(track_df, artist_df, lyric_df)

labeled_df = get_labeled_df(total_df, ['rock', 'hiphop', 'country'])
labeled_df = labeled_df.fillna(value='',axis=0)

save_pkl(labeled_df, 'labeled_df')
