import gensim
import gensim.downloader
from gensim.models.word2vec import Word2Vec
from gensim.models.keyedvectors import KeyedVectors
import numpy as np
import logging
from multiprocessing import cpu_count
import re

txtFile = 'philosophy_merge.txt'
kvFile = 'philosophy.kv'
vector_size = 50
epochs = 100

#lines=[]
sentences = []
with open(txtFile, 'r', encoding='utf8') as f:
    for line in f:
        l = line.strip().lower()
        if len(l) != 0 :
            #lines.append(l)
            tokens = re.split('\W+',  l)
            sentences.append(tokens)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
model = Word2Vec(
    sentences, #dataset, 
    min_count = 2,  #ignore rare words
    workers=cpu_count(), 
    vector_size=vector_size,
    epochs= epochs,
    negative=8,
    ns_exponent = 0.75
    )
model.wv.save(kvFile)
