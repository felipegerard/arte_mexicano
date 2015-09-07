
# coding=utf-8
## ES IMPORTANTE INDICAR EL ENCODING

import luigi
import os
import inspect
import re
import pickle
import unicodedata
from gensim import corpora, models, similarities

def remove_accents(input_str):
    if type(input_str) is not unicode:
        input_str = unicode(input_str, 'utf-8')
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

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
	input_dir = luigi.Parameter()
	clean_dir = luigi.Parameter()

	def requires(self):
		return [ InputText(self.input_dir + '/' + filename)
				for filename in os.listdir(self.input_dir) ]	
	
	def run(self):
		for inp, outp in zip(self.input(), self.output()):
			fi = inp.open('r')
			fo = outp.open('w')
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
		return [ luigi.LocalTarget(self.clean_dir + '/' + filename)
				for filename in os.listdir(self.input_dir) ]

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
		return CleanText(self.input_dir, self.clean_dir)

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
		print 'Run!!!'

	def output(self):
		return luigi.LocalTarget(self.model_dir + '/' + 'tf.pickle')

if __name__ == '__main__':
	luigi.run()











