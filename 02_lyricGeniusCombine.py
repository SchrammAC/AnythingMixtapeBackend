# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 00:48:05 2019

@author: night
"""

import os
import pandas as pd
import dill 

def save_pkl(df, filename):
    with open('data/'+filename+'.pkl','wb') as fobj:
        dill.dump(df,fobj)

from collections import defaultdict
lyric_dict = defaultdict(list)
directory = 'data/lyrics/'
for folder in os.listdir(directory):
    for file in os.listdir(directory+folder):
        outer_df = pd.read_json(directory+folder+'/'+file)
        lyric_dict['artist'].append(outer_df['artist'][0])
        inner_df = dict(outer_df['songs'][0])
        for key in inner_df.keys():
            lyric_dict[key].append(inner_df[key])
lyric_df = pd.DataFrame(lyric_dict)

save_pkl(lyric_df, 'lyric_dataset_190814')
        
