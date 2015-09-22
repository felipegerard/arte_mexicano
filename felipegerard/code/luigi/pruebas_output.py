
import pickle
from gensim.models import LdaModel
import os


with open('test/results/topic_results_stopwords_spanish_2.pickle') as f:
    a = pickle.load(f)

with open('test/results/topics_stopwords_spanish_2.pickle') as f:
    b = pickle.load(f)


l = LdaModel.load('test/models/lda-stopwords-spanish-2.lda')


u = [max(x, key=lambda y: y[1]) for x in a]
res = [(n,i,s,b[i]) for n,(i,s) in enumerate(u)]
d = os.listdir('test/txt/stopwords/spanish/')
res_d = {(num_topico, topico):[(num_libro, d[num_libro], score)]
		for num_libro, num_topico, score, topico in res}

res = {(num_topico, b[num_topico]):[]
		for num_libro, (num_topico, score) in enumerate(u)}


res = {i:{'topico':top, 'libros':[]} for i, top in enumerate(b)}
for num_libro, (num_topico, score) in enumerate(u):
	res[num_topico]['libros'].append((num_libro, d[num_libro], score))

for k, v in res.iteritems():
	print ''
	print v['topico']
	for l in v['libros']:
		print l