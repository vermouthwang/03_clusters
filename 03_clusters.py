import argparse
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from sklearn import cluster
from sklearn.cluster import DBSCAN
import pickle
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
from sklearn.metrics import pairwise_distances

#embeddingFile = 'merge2.pickle'
embeddingFile = "philo_word2vec.pickle"

sort_words_by_frequncy = False
limit_size = True
limit_count = 1000

#open word_vec pickle file
with open(embeddingFile, "rb") as f:
    word2vec = pickle.load(f)

# build a array contains all words' vectors for clustering
vectors = []
words = []
norms = []
for word in word2vec:
    vec = np.array(word2vec[word])
    # norm = vec/np.linalg.norm(vec)
    norm = np.linalg.norm(vec)
    normalized = vec/norm
    words.append(word)
    vectors.append(normalized)
    norms.append(norm)

# clusterarray = []
# for vecs in word2vec.values():
#     normalized = vecs/np.linalg.norm(vecs)
#     clusterarray.append(list(normalized))

print("clusterarray done")

# print(clusterarray[0])

# if sort_words_by_frequncy:
#     #sort vectors and words arrays by noårm in descending order
#     indices = np.argsort(norms)[::-1]
#     vectors = [vectors[i] for i in indices]
#     words = [words[i] for i in indices]


# n = limit_count if limit_size else len(vectors)
# print(len(vectors))
X = np.array(vectors)
# X = np.array(clusterarray)
# words = words[::]
X_embedded = TSNE(n_components=2, learning_rate='auto',init='random', perplexity=90, metric='cosine').fit_transform(X)
clustering = DBSCAN(eps=0.000001, min_samples=6,metric="cosine").fit(X_embedded)
# print("clustering done")

# precompute_distance = False
 
# if precompute_distance:
#     distance = pairwise_distances(X, metric='cosine')
#     X_embedded = TSNE(n_components=2, learning_rate='auto',init='random', perplexity=3, metric='precomputed').fit_transform(distance)
# else:
#     
# X_embedded = TSNE(n_components=2, learning_rate='auto',init='random', perplexity=40, metric='cosine').fit_transform(X) 
# clustering = DBSCAN(eps=0.0005, min_samples=5,metric="cosine").fit(X_embedded)
# #plot X_embedded with words
# plt.figure(figsize=(10, 10))
# for i, _ in enumerate(words):
#     x, y = X_embedded[i, :]
#     plt.scatter(x, y)
#     # plt.annotate(xy=(x, y), xytext=(0, 0), textcoords='offset points')
# plt.show()



# Do DBSCAN Cluster
# X = np.array([[-0.02003059,0.11112974,-0.66914636], [-0.5272778,0.9104893,-0.267949], [1.450222,1.3021897,-0.8128451],
#             [-1.6841936,-1.8068014,1.8529692], [0.17372763,-0.05740492,0.20767698]])

# # clustering = DBSCAN(eps=0.005, min_samples=5, metric = "cosine").fit(X)
# labels = clustering.labels_
# in_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
# # n_noise_ = list(labels).count(-1)
# # print("cluster done")
# # # print(clustering.labels_)

# unique_labels = set(labels)
# core_samples_mask = np.zeros_like(labels, dtype=bool)
# core_samples_mask[clustering.core_sample_indices_] = True

# colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
# for k, col in zip(unique_labels, colors):
#     if k == -1:
#         # Black used for noise.
#         col = [0, 0, 0, 1]

#     class_member_mask = labels == k

#     xy = X[class_member_mask & core_samples_mask]
#     plt.plot(
#         xy[:, 0],
#         xy[:, 1],
#         "o",
#         markerfacecolor=tuple(col),
#         markeredgecolor="k",
#         markersize=14,
#     )

#     xy = X[class_member_mask & ~core_samples_mask]
#     plt.plot(
#         xy[:, 0],
#         xy[:, 1],
#         "o",
#         markerfacecolor=tuple(col),
#         markeredgecolor="k",
#         markersize=6,
#     )

# plt.title(f"Estimated number of clusters: {n_clusters_}")
# plt.show()


# # Build a word to cluster score dictrionary
clusterscore = {}
i= 0
for word in word2vec:
    clusterscore[word] = clustering.labels_[i]
    i+=1
    # if i == 999:
    #     break
print("clusterscore dictionary done")

# write the word to cluster score dictionary into a pickle file
with open("word_2_score_0.pickle", "wb") as f:  
    pickle.dump(clusterscore, f)  
print("word to score pickle done")

# build a cluster result dictionary
cluster_result = {}
for word,score in clusterscore.items():
    if score in cluster_result:
        cluster_result[score].add(word)
    else:
        cluster_result[score] = {word}
print("cluster_result_dictionary_done")

with open("Cluster_results_0.000001_6_03.pickle",'wb') as file:
    pickle.dump(cluster_result, file)

     
# write the cluster result into a txt file
with open('Cluster_results_0.000001_6_03.txt','w') as file:
    for score, words in cluster_result.items():
        file.write('{}:{}\n'.format(score, words))

