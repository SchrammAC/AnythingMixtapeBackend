# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 11:09:35 2019

@author: night
"""
import os
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

fo = open("data/new_artist_list.txt", "r")
artist_list = fo.readlines()
fo.close()

import lyricsgenius
genius = lyricsgenius.Genius(access_token, timeout=10, sleep_time=1.5)
genius.remove_section_headers = True # Remove section headers (e.g. [Chorus]) from lyrics when searching
genius.skip_non_songs = False # Include hits thought to be non-songs (e.g. track lists)
genius.excluded_terms = ["(Remix)", "(Live)"] # Exclude songs with these words in their title
song = genius.search_song("To You", artist.name)
for artist_name in artist_list:
    stripped_name = artist_name.rstrip()
    artist = genius.search_artist(stripped_name, max_songs=50)
    if artist:
        with cd('data/lyrics'):
            try:
                os.mkdir(stripped_name)
            except FileExistsError:
                'Directory already exists'
            with cd(stripped_name):
                artist.save_lyrics(overwrite=True)
