# -*- coding: utf-8 -*-
"""
Created on Mon May  6 06:58:45 2019
Initial build of genre prediction model.
Parses 

@author: night
"""
import pandas as pd
import dill
import numpy as np
#from wordcloud import WordCloud, STOPWORDS

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import GridSearchCV
from sklearn import base

from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import ComplementNB
from sklearn.svm import SVC

from sklearn.neighbors import NearestNeighbors

class RowRemoveTransformer(base.BaseEstimator, base.TransformerMixin):
    
    def __init__(self, min_count=0):
        self.min_count = min_count  # We will need these in transform()
    
    def fit(self, X, y=None):
        # This transformer doesn't need to learn anything about the data,
        # so it can just return self without any further processing
        return self
    
    def transform(self, X):
        # Return an array with the same number of rows as X and one
        # column for each in self.col_names
        return [row for row in X if np.sum(row) > self.min_count]

def save_pkl(df, filename):
    with open('data/'+filename+'.pkl','wb') as fobj:
        dill.dump(df,fobj)
    
def load_pkl(filename):
    with open('data/'+filename+'.pkl','rb') as fobj:
        df = dill.load(fobj)
    return df

def generate_model(data):
    
    data = data.sample(frac=1).reset_index(drop=True)
    X = list(data.lyrics)
    y = list(data.genre)
    stop_words = frozenset(["verse", "chorus","instrumental"])
    
    lyric_class = Pipeline([
        ('ctvect', CountVectorizer(min_df=0, max_df=0.95, stop_words=stop_words)), #Vectorizer
        ('tfidf_trans', TfidfTransformer()), #Normalization
#        ('cnb', ComplementNB(alpha=0.1))
#        ('mnb', MultinomialNB())
        ('svc', SVC(probability=True))
    ])
        
#    parameters = {'mnb__alpha': [0.01, 0.03, 0.05, 0.08], 'ctvect__min_df': [0.1, 0.5, 0.02], 'ctvect__max_df': [0.99]}
    parameters = {'ctvect__min_df': [0.02], 'ctvect__max_df': [0.99], 'svc__C': [0.1, 1, 10]}
    gscv = GridSearchCV(lyric_class, parameters, cv=4)
    gscv.fit(X, y)
    print(gscv.best_params_)
    print(gscv.best_score_)
    
    lyric_clf = gscv.best_estimator_
        
    save_pkl(lyric_clf, 'svc_classifier_unigram')
    
    return lyric_clf

    
def classify_text(model, text):
    
    print(text)
    print(model.predict_proba(text))
    best_genre = model.predict(text)
    print(best_genre)
    return best_genre

def create_playlist(genre, data, input_text, vocab, num_tracks):
    genre_data = data.loc[data['genre']==genre[0]] #Select genre tracks
    tfidf_matrix = vectorize_it(genre_data, input_text, vocab)
    indices = get_closest_indices(tfidf_matrix,num_tracks)
    track_list = fetch_track_ids(genre_data,indices)
    return track_list
    
    
    
def vectorize_it(genre_data, input_text, vocab):
    input_df = pd.DataFrame(data=[['', input_text, '', '']], columns=['genre', 'lyrics', 'orig_index', 'track_id'])
    genre_data = genre_data.append(input_df, ignore_index=True)
    
    vector_trans = Pipeline([
        ('ctvect', CountVectorizer(vocabulary=vocab)),
#        ('rrt', RowRemoveTransformer()),
        ('tfidf_trans', TfidfTransformer())
    ])
        
#    text_vect = ctvect.fit_transform(genre_data.lyrics)
    
    return vector_trans.fit_transform(genre_data.lyrics)

    
def get_closest_indices(tfidf_matrix,num_tracks):
    nbrs = NearestNeighbors(n_neighbors=105).fit(tfidf_matrix)
    distances, indices = nbrs.kneighbors(tfidf_matrix[-1,:])
    indices=indices[distances>1] #Remove too-close matches (only 1 word in lyrics)
    indices = indices.flatten()[:num_tracks]
    return indices

def fetch_track_ids(genre_data,indices):
    similar_tracks = pd.Series(indices).map(genre_data.reset_index()['track_id'])
    return similar_tracks

def remove_empties(df):
    return df[df['lyrics'] != ' ']

    
data = load_pkl('labeled_df')
labels = pd.unique(data.genre)
data = remove_empties(data)

#try:
#    genre_clf = load_pkl('cnb_classifier5')
#except FileNotFoundError:
genre_clf = generate_model(data)

input_text = 'Just one more time before I go Ill let you know That all this time Ive been afraid Wouldnt let it show Nobody can save me now, no Nobody can save me now Stars are only visible in darkness Fear is ever-changing and evolving And I, Ive been poisoned inside But I, I feel so alive Nobody can save me now King is downed Its do or die Nobody can save me now The only sound Its the battle cry Its the battle cry Its the battle cry Nobody can save me now Its do or die Nobody can save me now King is downed Its do or die Nobody can save me now The only sound Its the battle cry Its the battle cry Its the battle cry Nobody can save me now Its do or die Just one more time before I go Ill let you know That all this time Ive been afraid Wouldnt let it show Nobody can save me now, no Nobody can save me now'

num_tracks=10

total_vocab = genre_clf.named_steps['ctvect'].vocabulary_

best_genre = classify_text(genre_clf, [input_text])

track_list = create_playlist(best_genre, data, input_text, total_vocab, num_tracks)

