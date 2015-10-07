# coding=utf-8

import pickle

with open('test/results/topic_results_stopwords_spanish_30.pickle') as f:
	tr = pickle.load(f)

with open('test/results/topics_stopwords_spanish_30.pickle') as f:
	t = pickle.load(f)

with open('test/results/document_results_stopwords_spanish_30.pickle') as f:
	dr = pickle.load(f)