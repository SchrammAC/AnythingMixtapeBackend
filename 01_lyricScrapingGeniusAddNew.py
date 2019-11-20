# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 11:09:35 2019

@author: night
"""
import os
import pandas as pd

from contextlib import contextmanager

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

fo = open("keys/genius_creds.nogit", "r")
client_id = fo.readline()
client_secret = fo.readline()
access_token = fo.readline()
fo.close()


new_artist_names = pd.read_csv('data/new-artist-list.csv')


#fo = open("data/190803_used_artist_list.txt", "r")
#used_artist_list = fo.readlines()
#fo.close()
#used_artist_list = [name.lower() for name in used_artist_list]


import lyricsgenius
genius = lyricsgenius.Genius(access_token, timeout=10, sleep_time=1.5)
genius.remove_section_headers = True # Remove section headers (e.g. [Chorus]) from lyrics when searching
genius.skip_non_songs = False # Include hits thought to be non-songs (e.g. track lists)
genius.excluded_terms = ["(Remix)", "(Live)"] # Exclude songs with these words in their title

for artist_name in new_artist_names['artist']:
    stripped_name = ' '.join(artist_name.split('-'))
#    if stripped_name not in used_artist_list:
    artist = genius.search_artist(stripped_name, max_songs=100)
#        used_artist_list.append(artist.name)
    if artist:
        with cd('data/lyrics'):
            try:
                os.mkdir(stripped_name)
            except FileExistsError:
                'Directory already exists'
            with cd(stripped_name):
                artist.save_lyrics(overwrite=True)
                    
#with open('data/190803_used_artist_list.txt', 'w') as f:
#    for item in used_artist_list:
#        f.write("%s\n" % item)
