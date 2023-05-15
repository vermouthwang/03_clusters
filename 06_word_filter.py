import nltk
from nltk.corpus import stopwords

import pickle
from PyDictionary import PyDictionary
 
# spell = SpellChecker()
with open("philo_freq_15000.pickle", "rb") as f:
    freq = pickle.load(f)

# build stopwords check list
nltk.download('stopwords')
stop_words = stopwords.words('english')
# print(stop_words)
other_invalide = ['has','will','more','must','one','two','three','four','five',
 "0o", "0s", "3a", "3b", "3d", "6b", "6o", "a", "a1", "a2",
"a3", "a4", "ab", "able", "about", "above", "abst", "ac",
"accordance", "according", "accordingly", "across", "act",
"actually", "ad", "added", "adj", "ae", "af", "affected"
, "affecting", "affects", "after", "afterwards", "ag",
 "again", "against", "ah", "ain", "ain't", "aj", "al",
 "all", "allow", "allows", "almost", "alone", "along", 
 "already", "also", "although", "always", "am", "among",
"amongst", "amoungst", "amount", "an", "and", "announce",
"another", "any", "anybody", "anyhow", "anymore", "anyone", 
"anyway", "anyways", "anywhere", "ao", "ap", "apart", "apparently", 
"appreciate", "appropriate", "approximately", "ar", "are", 
"aren", "arent", "aren't", "arise", "around", "as", "a's",
 "aside", "ask", "asking", "associated", "at", "au", "auth",
"av", "available", "aw", "away", "awfully", "ax", "ay", 
"az", "b", "b1", "b2", "b3", "ba", "back", "bc", "bd",
"be", "became", "because", "become", "becomes", 
"becoming", "been", "before", "beforehand", "begin", 
 "behind", "being", "below", "beside", "besides", "best", 
"better", "between", "beyond", "bi", "bill", 
"biol", "bj", "bk", "bl", "bn", "both", "bottom",
"bp", "br", "brief", "briefly", "bs", "bt", "bu", 
"but", "bx", "by", "c", "c1", "c2", "c3", "ca", 
"call", "came", "can", "cannot", "cant", "can't",
"cause", "causes", "cc", "cd", "ce", "certain", 
"certainly", "cf", "cg", "ch", "changes", "ci",
 "cit", "cj", "cl", "clearly", "cm", "c'mon", 
 "cn", "co", "com", "come", "comes", "con", 
 "consequently", "consider", "considering", 
 "contain", "containing", "contains", 
 "corresponding", "could", "couldn", "couldnt", 
 "couldn't", "course", "cp", "cq", "cr", "cry",
"cs", "c's", "ct", "cu", "currently", "cv", 
"cx", "cy", "cz", "d", "d2", "da", "date", "dc",
"dd", "de", "definitely", "describe", "described",
 "despite",  "df", "di", "did", "didn", "didn't","dj",
"dk", "dl", "do", "does", "doesn", "doesn't", 
"doing", "don", "done", "don't", "down", "downwards",
 "dp", "dr", "ds", "dt", "du", "due", "during", 
 "dx", "dy", "e", "e2", "e3", "ea", "each", "ec", 
 "ed", "edu", "ee", "ef", "effect", "eg", "ei", 
 "eight", "eighty", "either", "ej", "el", "eleven",
   "else", "elsewhere", "em", "empty", "en", "end", 
   "ending", "enough", "entirely", "eo", "ep", "eq",
     "er", "es", "especially", "est", "et", "et-al",
       "etc", "eu", "ev", "even", "ever", "every",'via','tre','sqq']
for other in other_invalide:
    if other not in stop_words:
        stop_words.append(other)

# check words and build a valid words list
validate_word = []
for freq_word in freq:
    if freq_word not in stop_words:
        for num in "1234567890":
            if num not in freq_word:
                validate_word.append(freq_word)
                break

# write pickle and text file
with open('philo_freq_valid.txt','w') as file:
    for words in validate_word:
        file.write('{}\n'.format(words))

with open("philo_freq_valid.pickle", "wb") as f:  
    pickle.dump(validate_word, f)  






# import gensim
# import gensim.downloader
# from gensim.models.word2vec import Word2Vec
# from gensim.models.keyedvectors import KeyedVectors
# import numpy as np
# import logging
# from multiprocessing import cpu_count
# import re
# from gensim.models.phrases import Phrases, Phraser
# import nltk
# from nltk.corpus import stopwords
# import os
# import pickle


# txtFile = '100.txt'
# kvFile = '100.kv'
# wordFreqFile = '100.pickle'
# vector_size = 100
# epochs = 100
 
# this_folder = os.path.dirname(os.path.abspath(__file__))
 
# txtFile = os.path.join(this_folder, txtFile)
# kvFile = os.path.join(this_folder, kvFile)
# wordFreqFile = os.path.join(this_folder, wordFreqFile)
 

# nltk.download('stopwords')
# nltk.download('punkt')
 
# stop_words = stopwords.words('english')
 
# def tokenize_text(text: str) -> str:
#     text = re.sub("[^A-Za-z]+", " ", text)
#     text = text.lower()
#     tokens = nltk.word_tokenize(text)
#     tokens = [w.strip() for w in tokens if not w in stop_words]
#     return tokens
 
# aa = tokenize_text('This is a test. This is another test. This is the last test.')
 
# min_sentence_len = 10
 
# #lines=[]
# sentences = []
# with open(txtFile, 'r', encoding='utf8') as f:
#     last_sentence = []
#     for line in f:
#         l = tokenize_text(line)
#         last_sentence.extend(l)
#         if len(last_sentence) > min_sentence_len:
#             sentences.append(last_sentence)
#             last_sentence = []
 
# #optional to detect bigrams
# # phrases = Phrases(sentences, min_count=30, progress_per=10000)
# # bigram = Phraser(phrases)
# # sentences = bigram[sentences]
 
# word_freq = dict()
# for sent in sentences:
#     for i in sent:
#         if i in word_freq:
#             word_freq[i] += 1
#         else:
#             word_freq[i] = 1
# len(word_freq)
 
# freq_words = sorted(word_freq, key=word_freq.get, reverse=True)
# print(freq_words[:50])
# #pickle the word_freq
# with open(wordFreqFile, "wb") as f:
#     pickle.dump(word_freq, f)
 

# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
# model = Word2Vec(
#     sentences, #dataset,
#     min_count = 3,  #ignore rare words
#     workers=cpu_count(),
#     vector_size=vector_size,
#     window=5, #window size
#     epochs= epochs,
#     hs = 0, #negative sampling=0 | hierarchical softmax=1 , hierarchical softmax tends to be better for infrequent words, while negative sampling works better for frequent words and lower dimensional vectors.
#     negative=5, #negative sampling
#     ns_exponent=0.75, #negative sampling exponent
#     sg = 1, #CBOW=0 | Skip-gram=1 , skip-gram works better with infrequent words
#     )
# model.wv.save(kvFile)