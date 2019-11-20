# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 10:39:07 2019

@author: night
"""

import pandas as pd
import re
import requests
import base64
import six
import json
from retrying import retry
import time
import dill
#from requests_futures.sessions import FuturesSession

f = open("keys/spotify.nogit", "r")
client_id = f.readline().strip('\n')
client_secret = f.readline()
f.close()

art_filenm = 'data/artist-list-total.csv'
song_filenm = 'data/trigenre-lyrics-total-clean-new.csv'

search_url = 'https://api.spotify.com/v1/search'

def save_pkl(df, filename):
    with open('data/'+filename+'.pkl','wb') as fobj:
        dill.dump(df,fobj)
    
def load_pkl(filename):
    with open('data/'+filename+'.pkl','rb') as fobj:
        df = dill.load(fobj)
    return df

def load_data(art_filenm, song_filenm):
    artist_list = pd.read_csv(art_filenm,encoding = "ISO-8859-1")
    song_list = pd.read_csv(song_filenm,encoding = "ISO-8859-1")
    return artist_list, song_list

def get_token(client_id,client_secret):
    url='https://accounts.spotify.com/api/token'
    params = {'grant_type' : 'client_credentials'}
    auth_header = base64.b64encode(six.text_type(client_id + ':' + client_secret).encode('ascii'))
    headers = {"Authorization": "Basic {}".format(auth_header.decode('ascii'))}
    response=requests.post(url, data=params, headers=headers)
    response_data = json.loads(response.text)
    return response_data['access_token']

#@retry(stop_max_attempt_number=3)
def get_artist_info(track_df, token):
    headers = {'Accept':'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(token)}
    artist_info = {}
    artist_compare = []
    i=0
    k=0
    badlist = []
#    for artist in artist_list.artist: 
    artist_list = list(track_df['artist'].unique())
    while i < len(artist_list):
        #artist_q = re.sub('-', ' ', artist)
        artist_q = artist_list[i]
        params = {'q' : artist_q, 'type' : 'artist', 'limit':1}
        response=requests.get(search_url, params=params, headers=headers) 
        res = json.loads(response.text)
        if response.status_code == 200:
            try:
                artist_data = res['artists']['items'][0]
                artist_info[i] = artist_data
            except IndexError:
                print(f'No result for {artist_list[i]}')
                badlist.append(i)
            i = i+1
        elif response.status_code == 401:
            token = get_token(client_id,client_secret)
        
        elif response.status_code == 429:
            print("Rate exceeded. Waiting 5 seconds")
            time.sleep(5)
        else:
            k = k+1
            if k > 3:
                k=0
                print(i)
                i += 1
        
    return artist_info, artist_compare

#@retry(stop_max_attempt_number=3)
def get_track_info(track_df, token):
    headers = {'Accept':'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(token)}
    song_info = {}
    i=0
    k=0
    badlist = []
    i = 20000
    while i < len(track_df)+20000:
        if i%100==0:
            print(f'Done with song {i}')
        artist_q = track_df['artist'][i]
        song_q = track_df['title'][i]
        all_q = 'artist:' + artist_q + ' track:' + song_q
        params = {'q' : all_q, 'type' : 'track', 'limit':1}
        response=requests.get(search_url, params=params, headers=headers) 
        res = json.loads(response.text)
        if response.status_code == 200:
            try:
                song_data = res['tracks']['items'][0]
                song_info[i] = song_data
            except IndexError:
                print(f'No result for {track_df.title[i]} by {track_df.artist[i]}')
                badlist.append(i)
            i = i+1
        elif response.status_code == 401:
            token = get_token(client_id,client_secret)
        
        elif response.status_code == 429:
            print("Rate exceeded. Waiting 5 seconds")
            time.sleep(5)
        else:
            k = k+1
            if k > 3:
                k=0
                print(i)
                i += 1
    return song_info, badlist

def trackInfoToDF(track_info):
    name = []
    artist = []
    artist_id = []
    album = []
    album_type = []
    track_id = []
    popularity = []
    orig_index = []
    for key in track_info.keys():
        name.append(track_info[key]['name'])
        artist.append(track_info[key]['artists'][0]['name'])
        artist_id.append(track_info[key]['artists'][0]['id'])
        album.append(track_info[key]['album']['name'])
        album_type.append(track_info[key]['album']['album_type'])
        track_id.append(track_info[key]['id'])
        popularity.append(track_info[key]['popularity'])
        orig_index.append(key)
        
    return pd.DataFrame(list(zip(orig_index,name,artist,artist_id,album,album_type,track_id,popularity)), columns = ['orig_index','name','artist','artist_id','album','album_type','track_id','popularity'])
    

def artistInfoToDF(artist_info):
    artist = []
    artist_id = []
    genres = []
    popularity = []
    orig_index = []
    for key in artist_info.keys():
        artist.append(artist_info[key]['name'])
        artist_id.append(artist_info[key]['id'])
        genres.append(artist_info[key]['genres'])
        popularity.append(artist_info[key]['popularity'])
        orig_index.append(key)

    return pd.DataFrame(list(zip(artist,artist_id,genres,popularity)), columns = ['artist','artist_id','genres','popularity'])


lyric_df = load_pkl('lyric_dataset_190814')

token = get_token(client_id,client_secret)


#supp_artist_list = pd.DataFrame({'artist':['ti', 'russell dickerson', 'sixx am', 'plain white ts']})
#artist_info_supp, artist_compare_supp = get_artist_info(supp_artist_list,token)


#artist_info, artist_compare = get_artist_info(lyric_df, token)
#artist_df = artistInfoToDF(artist_info)
#save_pkl(artist_df, 'artist_df')
#lyric_df_a = lyric_df.iloc[0:20000]
#lyric_df_b = lyric_df.iloc[20000:]
#
#track_info_a, badlist = get_track_info(lyric_df_a, token)
#track_info_b, badlist_b = get_track_info(lyric_df_b, token)
#track_info = pd.concat([track_info_a, track_info_b])
#save_pkl(track_info, 'track_dict_all')
##

#
track_df_total = trackInfoToDF(track_info_a)
track_df_nodup = track_df_total.drop_duplicates(subset='track_id')
save_pkl(track_df_nodup, 'track_df')

