import pickle
cluster_file = "cluster_results2_0.4_7.pickle"
with open(cluster_file, "rb") as f:
    word2vec = pickle.load(f)

len_array = []
for scores,words in word2vec.items():
    len_array.append(len(words))

print(len_array)