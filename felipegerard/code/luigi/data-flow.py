
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

# Quitar caracteres con acentos
def remove_accents(input_str):
    if type(input_str) is not unicode:
        input_str = unicode(input_str, 'utf-8')
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

# Iterar sobre un corpus
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

# Imports UNAM
try:
	from cStringIO import StringIO
except:
	from StringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from nltk import wordpunct_tokenize
from nltk.corpus import stopwords



# Input PDF
class InputPDF(luigi.ExternalTask):
	filename = luigi.Parameter()
	def output(self):
		return luigi.LocalTarget(self.filename)


# Input book
execfile('functions/pdf2txt.py')

class ReadText(luigi.Task):
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	outputs = []

	def requires(self):
		return [InputPDF(self.pdf_dir + '/' + book_name)
			for book_name in os.listdir(self.pdf_dir)]
			#  \
			# for f in os.listdir(self.pdf_dir + '/' + book_name)]
		
	def run(self):
		if not os.path.exists(self.txt_dir):
			print "Creando carpeta base para archivos txt."
			os.makedirs(self.txt_dir)
		librosNoConvertidos = []
		self.outputs = extraerVolumenes(self.input(),self.txt_dir,librosNoConvertidos)
		with open(self.txt_dir + '/' + 'librosNoConvertidos.txt', 'w') as f:
			f.writelines(librosNoConvertidos)
		print self.outputs
	
	def output(self):
		return [luigi.LocalTarget(book) for book in self.outputs]


# Limpiar texto ### FALTA

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

# Generar diccionario
execfile('functions/GeneradorDiccionario.py')
execfile('functions/GeneradorCorpus.py')
execfile('functions/TopicModeling.py')

class GenerateDictionary(luigi.Task):
	"""docstring for CleanText"""
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	model_dir = luigi.Parameter()
	min_docs_per_lang = luigi.IntParameter(default=1)

	def requires(self):
		return ReadText(self.pdf_dir, self.txt_dir)	
	
	def run(self):
		idiomas_omitidos = ['swedish']
		idiomas = os.listdir(self.txt_dir)
		idiomas = [idioma for idioma in idiomas \
			if '.' not in idioma \
				and idioma not in idiomas_omitidos]
		for idioma in idiomas:
			print '=========================='
			print 'Generando ' + idioma
			rutaTextos = os.path.join(self.txt_dir,idioma)
			if len(os.listdir(rutaTextos)) < self.min_docs_per_lang:
				logging.info("No hay suficientes muestras para generar el modelo. Omitiendo idioma.")
				print "No hay suficientes muestras para generar el modelo. Omitiendo idioma."
				continue
			elif not os.path.exists(self.model_dir):
				print "Creando carpeta base para modelos."
				os.makedirs(self.model_dir)
			listaArchivos = generarDiccionario(rutaTextos, self.model_dir, 6, idioma)
			generarCorpus(rutaTextos, self.model_dir, 6, idioma)
			

		with self.output().open('w') as f:
			f.write('\n'.join(idiomas) + '\n')

	def output(self):
		# return luigi.LocalTarget(self.clean_dir + '/' + 'prueba.txt')
		return luigi.LocalTarget(self.txt_dir + '/idiomas.txt')


# class GenerateDictionary(luigi.Task):
# 	"""Docstring"""
# 	input_dir = luigi.Parameter()
# 	clean_dir = luigi.Parameter()
# 	model_dir = luigi.Parameter()

# 	def requires(self):
# 		return [CleanText(self.input_dir + '/' + i, self.clean_dir + '/' + i) for i in os.listdir(self.input_dir)]

# 	def run(self):
# 		if not os.path.exists(self.clean_dir):
# 			print "Creando carpeta base para archivos txt."
# 			os.makedirs(self.clean_dir)
# 		dictionary = corpora.Dictionary(doc.open('r').read().split() for doc in self.input())
# 		once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq <= 1]
# 		dictionary.filter_tokens(once_ids) # remove words that appear only once
# 		dictionary.compactify()
# 		f = self.output().open('w')
# 		pickle.dump(dictionary, f)
# 		f.close()

# 	def output(self):
# 		return luigi.LocalTarget(self.model_dir + '/' + 'dictionary.pickle')

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
		print 'Loading Transform'
		print '==========================='
		with self.input().open('r') as f:
			tfidf_transform = pickle.load(f)
		print 'Loading Corpus'
		print '==========================='
		corpus = corpora.MmCorpus(self.model_dir + '/' + 'corpus.mmkt')
		print 'Creating Index'
		print '==========================='
		index = similarities.MatrixSimilarity(tfidf_transform[corpus])
		#index.save(self.model_dir + '/' + 'index.pickle')

		print 'Calculating Similarities'
		print '==========================='
		sims = []
		i = 1
		for doc in corpus:
			i = i + 1
			print i
			doc_tfidf = tfidf_transform[doc]
			sim = sorted(enumerate(index[doc_tfidf]), key = lambda item: item[1], reverse=True)
			sims.append(sim[:self.num_sim_docs])
			#print sims[:self.num_sim_docs]
		with self.output().open('w') as f:
			pickle.dump(sims, f)

	def output(self):
		return luigi.LocalTarget(self.model_dir + '/' + 'similarities.pickle')


if __name__ == '__main__':
	luigi.run()











