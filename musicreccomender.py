# -*- coding: utf-8 -*-
"""MusicReccomender.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ifEpZdp8LLv-xAUI2PtZXvd_y-NV3wB9

Thanks https://www.kaggle.com/artempozdniakov/spotify-data-eda-and-music-recommendation and https://www.kaggle.com/vatsalmavani/music-recommendation-system-using-spotify-dataset for good reference. (First time ever building K-Means Clustering that finds data based of other points!)

Uploading Data
"""


"""Data Preprocessing and Visualization"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split

df = pd.read_csv("data.csv")

df["artists"]

df.head()

df.isna().sum()

df2 = df.drop(["artists", "name", "id", "release_date", "year"], axis=1)

"""K_Means Clustering (Intertia)"""

clusters = range(1, 11)
inertia = []
data = df2.to_numpy()
for i in clusters:
  k_means = KMeans(n_clusters=i)
  k_clusters = k_means.fit_predict(data)
  inertia.append(k_means.inertia_)

# plt.plot(clusters, inertia, 'bx-')
# plt.xlabel('k')
# plt.ylabel('Inertia')
# plt.show()

print(k_means.labels_)

df2 = df.drop(["artists", "name", "id", "release_date", "year"], axis=1)
df2["cluster"] = k_clusters
df2.head()

"""K_Means Clustering on a Scatter Plot"""

# sns.lmplot(x='acousticness', y='loudness', data=df2, hue='cluster', fit_reg=False)

# sns.pairplot(df2)

# sns.pairplot(df2, hue="cluster")

# fig, ax = plt.subplots(figsize=(13,13))    
# sns.heatmap(df2.corr(), annot=True, square=True, ax=ax)
# ax.plot()

pca = PCA(2)
pca.fit(df2)

pca_data = pd.DataFrame(pca.transform(df2))
pca_data.head()

pca_means = KMeans(n_clusters=10)
pca_data = pca_data.values
df2 = df.drop(["artists", "name", "id", "release_date", "year"], axis=1)
df2["cluster"] = k_clusters
df2 = df2.values
y_kmeans = pca_means.fit(df2)
y_kmeans = pca_means.predict(df2)
# print(y_kmeans)
# y_kmeans = pd.DataFrame(y_kmeans)
# y_kmeans = y_kmeans.values

u_labels = np.unique(y_kmeans)

# for i in u_labels:
#     plt.scatter(pca_data[y_kmeans == i , 0] , pca_data[y_kmeans == i , 1], label = i)
# plt.legend()
# plt.show()

scaler = MinMaxScaler()
df2 = df.drop(["artists", "name", "id", "release_date", "year"], axis=1)
df2["cluster"] = k_clusters
scaled_df = scaler.fit_transform(df2)

scaled_df = pd.DataFrame(scaled_df, columns=df2.columns)
print(scaled_df.head())

scaled_df.shape

scaled_df.insert(1, "artists", df["artists"], True )
scaled_df.insert(6, "id", df["id"], True)
scaled_df.insert(12, "name", df["name"], True)
scaled_df.insert(14, "release_date", df["release_date"], True)
scaled_df.insert(18, "year", df["year"], True)
scaled_df.head()

def scaled_data_get():
  return scaled_df


"""Spotify Song Reccomendation System"""

# from tqdm import tqdm
def recommend_songs(data, song, num_of_recommendations):
  song = data[data.name.str.lower() == song.lower()].head(1)
  song = song.drop(["artists", "name", "id", "release_date", "year"], axis=1)
  song = song.values[0]
  dists = []
  data = data.drop_duplicates(subset="name", keep="first", inplace=False)
  data = data.drop(["artists", "name", "id", "release_date", "year"], axis=1)
  for song_to_rec in data.values:
    dist = 0
    for col in range(len(data.columns)):
      dist = dist + np.absolute((float(song[col]) - (song_to_rec[col])))
    dists.append(dist)
  data.insert(1, "artists", df["artists"], True )
  data.insert(6, "id", df["id"], True)
  data.insert(12, "name", df["name"], True)
  data.insert(14, "release_date", df["release_date"], True)
  data.insert(18, "year", df["year"], True)
  data["dists"] = dists
  data = data.sort_values("dists")
  return data[["artists", "name", "year", "cluster"]][1:num_of_recommendations]

recommend_songs(scaled_df, "The Way Life Goes (feat. Oh Wonder)", 10)

recommend_songs(scaled_df, "Before You Go", 6)

recommend_songs(scaled_df, "Magic In The Hamptons (feat. Lil Yachty)", 26)



from sklearn.model_selection import train_test_split
def predict_feature_dataset(feature, t_size):
  scaled_df = scaled_data_get()
  data = ['acousticness', 'danceability', 'duration_ms', 'energy', 'explicit', 
        'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'speechiness',
        'tempo', 'valence']

  for sub_feature in data:
    if feature == sub_feature:
      data.pop(sub_feature)
  feature = [feature]

  X = scaled_df[data]
  y = scaled_df[feature]

  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=t_size)

  return X_train, X_test, y_train, y_test

  













"""Popularity Prediction Model"""
from xgboost import XGBRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold
from numpy import mean
from numpy import std
from sklearn.ensemble import StackingRegressor

X = scaled_df[['acousticness', 'danceability', 'duration_ms', 'energy', 'explicit', 
        'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'speechiness',
        'tempo', 'valence']]
y = scaled_df["popularity"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

def get_models():
  models = {}
  models["xgb"] = XGBRegressor()
  models["lr"] = LinearRegression()
  models["dtr"] = DecisionTreeRegressor()
  models["svr"] = SVR()
  models["knn"] = KNeighborsRegressor()
  return models

def eval_model(model, X, y):
  rkf = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
  scores = cross_val_score(model, X, y, scoring='neg_mean_absolute_error', cv=rkf, n_jobs=-1, error_score='raise')
  return scores

model_scores = []
model_names = []

# models = get_models()
# for name, model in models.items():
#   score = eval_model(model, X_train, y_train)
#   model_scores.append(score)
#   model_names.append(name)
#   print(f"Model: {name}, Score = {mean(score)}, {std(score)}")

def stacked_model():
  level0 = []
  level0.append(("xgb", XGBRegressor()))
  level0.append(('dtr', DecisionTreeRegressor()))
  level0.append(('svr', SVR()))
  level0.append(('knn', KNeighborsRegressor()))
  level1 = LinearRegression()
  model = StackingRegressor(estimators=level0, final_estimator=level1, cv=5, verbose=2)
  return model

def fit_to_dataset(X, y):
  model = stacked_model()
  model.fit(X, y)

  return model

model = fit_to_dataset(X_train, y_train)

import pickle                                                             
filename = 'popularity_predictor.sav'
pickle.dump(model, open(filename, 'wb'))

with open(filename, "rb") as file:
  model = pickle.load(file)



from sklearn.cross_validation import cross_val_score
train_score = cross_val_score(reg, X_train, y_train, scoring="neg_mean_squared_error")
print(f"Train Score: {train_score}")
test_score = cross_val_score(reg, X_test, y_test, scoring="neg_mean_squared_error")
print(f"Test Score: {test_score}")