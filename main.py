import numpy as np
import pandas as pd
import string
import re
import nltk
from sklearn.model_selection import train_test_split
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import GridSearchCV


d1 = pd.read_csv(r'D:/Internship Luminar/Cyber bullying_tweets/cyberbullying_tweets.csv')

nltk.download('wordnet')

stop_words = set(stopwords.words('english'))
def clear(text):
    text = re.sub(r'@[A-Za-z0-9]+','',text)
    text = re.sub(r'RT[\s]+','',text)
    text = re.sub(r'https?:\/\/\S+','',text)
    text = re.sub(r'#','',text)

    return text

d1['tweet_text'] = d1['tweet_text'].apply(clear)
d1['tweet_text'] = d1['tweet_text'].str.replace("[^a-zA-Z@]",' ')

d1['tweet_text'] = d1['tweet_text'].apply(lambda x: ' '.join([w for w in x.split() if len(w)>3]))

tokenizer = RegexpTokenizer(r'\w+')
d1['tweet_text'] = d1['tweet_text'].apply(lambda x: tokenizer.tokenize(x.lower()))


stemmer = PorterStemmer()
def word_stemmer(text):
    stem_text = " ".join([stemmer.stem(i) for i in text])
    return stem_text

d1['tweet_text'] = d1['tweet_text'].apply(lambda x: word_stemmer(x))


lemmatizer = WordNetLemmatizer()
def word_lemmatizer(text):
    lem_text = [lemmatizer.lemmatize(i) for i in text]
    return lem_text

d1['tweet_text'].apply(lambda x: word_lemmatizer(x))
d1.head()
d1['tweet_text'].duplicated().sum()
d1.drop_duplicates('tweet_text', inplace = True)
d1['cyberbullying_type'] = d1['cyberbullying_type'].replace(to_replace=['gender','other_cyberbullying','age','ethnicity'],value = 'Bullying')
d1['cyberbullying_type'] = d1['cyberbullying_type'].map({'not_cyberbullying':0,'Bullying':1})
d1['cyberbullying_type'].fillna(0,inplace=True)
d1['tweet_text'].fillna('',inplace=True)
X = d1['tweet_text']  
y = d1['cyberbullying_type'] 

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.1, random_state = 42)


tfidf = TfidfVectorizer(max_features = 5000)
X_train_tf = tfidf.fit_transform(X_train)
X_test_tf = tfidf.transform(X_test)  

print(X_train_tf.shape)
print(X_test_tf.shape)

import pickle

with open('tfidf_vectorization','wb') as f:
    pickle.dump(tfidf,f)

logic = LogisticRegression()
logic.fit(X_train_tf,y_train)
pred = logic.predict(X_test_tf)

with open('model','wb') as f:
    pickle.dump(logic,f)