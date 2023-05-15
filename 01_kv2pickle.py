
from gensim.models.keyedvectors import KeyedVectors
import pickle

kvFile = 'philosophy.kv'
wordFile = 'philo_freq_valid.pickle'
embeddingFile = 'philo_word2vec.pickle'

model =  KeyedVectors.load(kvFile)
embedding_dict = {}

with open(wordFile, "rb") as f:
    freq_word = pickle.load(f)
# with open(wordFile, encoding='utf8') as file:
#     lines = file.readlines()
#     n = len(lines)
#     for i,line in enumerate(lines):        
#         id, word = line.split()
#         print(f'{i}/{n} {word}')
    for word in freq_word:
        try:
            embedding_dict[word] = model[word]
        except:
            pass

with open(embeddingFile, "wb") as f:  
    pickle.dump(embedding_dict, f)  

print(len(embedding_dict))
# with open('movieid_2_vec.txt','w') as file:
# # file.write('{}\n'.format(len(id2entity)))
#     for word, vec in embedding_dict.items():
#         file.write('{}:{}\n'.format(word, vec))