# -*- coding: utf-8 -*-
"""
Code to clean lyric database

Removes total duplicates (same artist, title) before and after
   cleaning up underscores.
Removes all songs that contain another title from the same artist. 
   (e.g. songtitle kept, songtitle_remix removed)
Removes occurances of artist name from lyrics.

@author: Anthony Schramm
"""
import pandas as pd
import re
import dill

def save_pkl(df, filename):
    with open('data/'+filename+'.pkl','wb') as fobj:
        dill.dump(df,fobj)
    
def load_pkl(filename):
    with open('data/'+filename+'.pkl','rb') as fobj:
        df = dill.load(fobj)
    return df


song_info = load_pkl('lyric_dataset_190814')
new_filename = 'data/lyric_dataset_190814_clean.csv'


unique_artist = song_info.artist.unique()
clean_song_info = pd.DataFrame()

for artist in unique_artist:
    art_split= artist.split('-')
    art_df = song_info[song_info.artist == artist]
    art_df = art_df.drop_duplicates(subset=['artist', 'title'], keep=False)

  
    #find and remove duplicates and missing lyrics from temporary df
    badlyric = 'Lyrics for this song have yet to be released.'
    for song in art_df['title']:
        for i in art_df.index:
            if i in art_df.index:
                #Song title within another song, but not the same song
                if badlyric in art_df['lyrics'][i]:
                    art_df = art_df.drop(i)
                elif ((song in art_df['title'][i]) & (song != art_df['title'][i])):
                    art_df = art_df.drop(i)
    
    
    for i in range(0,len(art_df.lyrics)):
        #Remove everything contained in brackets
        lyric = art_df.iloc[i]['lyrics']
        artist = art_df.iloc[i]['artist']
        brackpat = re.compile("\[.*?\]")
        new_lyric = re.sub(brackpat, ' ', lyric)
        
        
        
        for name in art_split:
            new_lyric = re.sub(name, "", new_lyric, flags=re.IGNORECASE)
        
        art_df.iloc[i]['lyrics'] = new_lyric
        
    
    #append to new df / append to new file
    clean_song_info = pd.concat([clean_song_info, art_df], ignore_index=True)
    
save_pkl(clean_song_info,'track_lyrics')









