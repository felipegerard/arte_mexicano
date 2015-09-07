
# coding=utf-8
## ES IMPORTANTE INDICAR EL ENCODING

import luigi
import os
import inspect
import re
import pickle
import unicodedata
from gensim import corpora, models, similarities

# ----------------------------------------------------------------
# Funciones y clases adicionales

def remove_accents(input_str):
    if type(input_str) is not unicode:
        input_str = unicode(input_str, 'utf-8')
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

class CorpusIterator(object):
    def __init__(self, dir):
        '''dir debe contener los documentos limpios'''
        self.dir = dir
        self.dir_list = os.listdir(self.dir)
    
    def __iter__(self):
        for doc in self.dir_list:
            f = open(self.dir + '/' + doc)
            d = f.read() #.decode('utf-8')
            f.close()
            yield d

# ----------------------------------------------------------------
# Data Flow

class InputText(luigi.ExternalTask):
    """
    This class represents something that was created elsewhere by an external process,
    so all we want to do is to implement the output method.
    """
    filename = luigi.Parameter()

    def output(self):
        """
        Returns the target output for this task.
        In this case, it expects a file to be present in the local file system.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """

        # The directory containing this file
        root = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "/"
        return luigi.LocalTarget(root + self.filename)

class CleanText(luigi.Task):
	"""docstring for CleanText"""
	input_file = luigi.Parameter()
	clean_file = luigi.Parameter()

	def requires(self):
		return InputText(self.input_file)	
	
	def run(self):
		fi = self.input().open('r')
		fo = self.output().open('w')
		txt = fi.read()#.decode('utf-8')
		#txt = unicode(txt, 'utf-8') ### <-- This doesnt work either
		txt = self.clean_text(txt)
		# print txt[:100].encode('utf-8')
		# print '---------------------------------------------'
		fo.write(txt)
		fi.close()
		fo.close()

	def output(self):
		# return luigi.LocalTarget(self.clean_dir + '/' + 'prueba.txt')
		return luigi.LocalTarget(self.clean_file)

	def clean_text(self, d):
	    '''d debe ser un string'''
	    d = remove_accents(d)
	    d = re.sub('\n', ' ', d)
	    d = d.lower()
	    d = re.sub('[^a-z0-9 ]', ' ', d)
	    d = re.sub(' +', ' ', d)
	    d = re.sub(' ([^ ]{1,3} )+', ' ', d, )
	    d = re.sub(' [^ ]*(.)\\1{2,}[^ ]* ', ' ', d)
	    return d


class GenerateDictionary(luigi.Task):
	"""Docstring"""
	input_dir = luigi.Parameter()
	clean_dir = luigi.Parameter()
	model_dir = luigi.Parameter()

	def requires(self):
		return [CleanText(self.input_dir + '/' + i, self.clean_dir + '/' + i) for i in os.listdir(self.input_dir)]

	def run(self):
		dictionary = corpora.Dictionary(doc.open('r').read().split() for doc in self.input())
		once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq <= 1]
		dictionary.filter_tokens(once_ids) # remove words that appear only once
		dictionary.compactify()
		f = self.output().open('w')
		pickle.dump(dictionary, f)
		f.close()

	def output(self):
		return luigi.LocalTarget(self.model_dir + '/' + 'dictionary.pickle')

class Vectorize(luigi.Task):
	"""Docstring"""
	input_dir = luigi.Parameter()
	clean_dir = luigi.Parameter()
	model_dir = luigi.Parameter()

	def requires(self):
		return GenerateDictionary(self.input_dir, self.clean_dir, self.model_dir)

	def run(self):
		with self.input().open('r') as f:
			dictionary = pickle.load(f)
		print dictionary
		corpus_iterator = CorpusIterator(self.clean_dir)
		corpus_bow = [dictionary.doc2bow(d.split()) for d in corpus_iterator]
		corpora.MmCorpus.serialize(self.model_dir + '/' + 'corpus.mmkt', corpus_bow)

	def output(self):
		return luigi.LocalTarget(self.model_dir + '/' + 'corpus.mmkt')

class TransformTFIDF(luigi.Task):
	"""Docstring"""
	input_dir = luigi.Parameter()
	clean_dir = luigi.Parameter()
	model_dir = luigi.Parameter()

	def requires(self):
		return Vectorize(self.input_dir, self.clean_dir, self.model_dir)

	def run(self):
		corpus = corpora.MmCorpus(self.model_dir + '/' + 'corpus.mmkt')
		tfidf_transform = models.TfidfModel(corpus)
		with self.output().open('w') as f:
			pickle.dump(tfidf_transform, f)

	def output(self):
		return luigi.LocalTarget(self.model_dir + '/' + 'tfidf_transform.pickle')

class DocumentSimilarities(luigi.Task):
	"""Docstring"""
	input_dir = luigi.Parameter()
	clean_dir = luigi.Parameter()
	model_dir = luigi.Parameter()
	num_sim_docs = luigi.IntParameter(default=5)

	def requires(self):
		return TransformTFIDF(self.input_dir, self.clean_dir, self.model_dir)

	def run(self):
		with self.input().open('r') as f:
			tfidf_transform = pickle.load(f)
		corpus = corpora.MmCorpus(self.model_dir + '/' + 'corpus.mmkt')
		corpus_tfidf = tfidf_transform[corpus]
		index = similarities.MatrixSimilarity(corpus_tfidf)
		index.save(self.model_dir + '/' + 'index.pickle')

		sims = []
		iter = 1
		for doc in corpus_tfidf:
			iter = iter + 1
			print iter
			sim = sorted(enumerate(index[doc]), key = lambda item: item[1], reverse=True)
			sims.append(sim[:self.num_sim_docs])
			#print sims[:self.num_sim_docs]
		with self.output()['similarities'].open('w') as f:
			pickle.dump(sims, f)

	def output(self):
		return {'index':luigi.LocalTarget(self.model_dir + '/' + 'index.pickle'),\
				'similarities':luigi.LocalTarget(self.model_dir + '/' + 'similarities.pickle')}


if __name__ == '__main__':
	luigi.run()











