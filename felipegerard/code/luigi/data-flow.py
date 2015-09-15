
# coding=utf-8
## ES IMPORTANTE INDICAR EL ENCODING

import luigi
import os
import inspect
import re
import pickle
import unicodedata
#from gensim import corpora, models, similarities

import shutil
from pprint import pprint

# execfile('functions/TopicModeling.py')
# import time, datetime

execfile('functions/helper_functions.py')


# ----------------------------------------------------------------
# Data Flow


# Input PDF directory
class InputPDF(luigi.ExternalTask):
	filename = luigi.Parameter()
	def output(self):
		return luigi.LocalTarget(self.filename)

# Input book
class ReadText(luigi.Task):
	book_name = luigi.Parameter()
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	meta_dir = luigi.Parameter(default='meta')
	meta_file = luigi.Parameter(default='librosAgregados.tm')

	def requires(self):
		pdf_bookdir = os.path.join(self.pdf_dir, self.book_name)
		return InputPDF(pdf_bookdir)

	def output(self):
		metafile = os.path.join(self.txt_dir,'meta',self.book_name+'.meta')
		return luigi.LocalTarget(metafile)
		
	def run(self):
		# Extraer textos
		idioma, contenido = extraerVolumen(self.input())
		if not os.path.exists(self.txt_dir + '/' + idioma):
			os.mkdir(self.txt_dir + '/' + idioma)
			print '--------------------'
			print 'Creando carpeta de ' + idioma

		book_path = os.path.join(self.txt_dir,idioma,self.book_name+'.txt')
		with open(book_path, 'w') as f:
			f.write(contenido)
		print self.book_name + ' --> ' + idioma
		with self.output().open('w') as f:
			f.write(idioma)

		# Guardar los metadatos
		guardarMetadatos(self.book_name,idioma,self.txt_dir,self.meta_file)
	

# Meter a carpetas de idioma. Si no hacemos esto entonces no es idempotente
class DetectLanguages(luigi.Task):
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	meta_dir = luigi.Parameter(default='meta')
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	lang_file = luigi.Parameter(default='idiomas.tm')

	def requires(self):
		return [ReadText(book_name, self.pdf_dir, self.txt_dir, self.meta_dir, self.meta_file) for book_name in os.listdir(self.pdf_dir)]

	def output(self):
		metapath = os.path.join(self.txt_dir,self.lang_file)
		return {'langs':luigi.LocalTarget(metapath),
				'files':self.input()}
		
	def run(self):
		idiomas = set()
		for p in os.listdir(os.path.join(self.txt_dir,self.meta_dir)):
			p = os.path.join(self.txt_dir, self.meta_dir, p)
			with open(p, 'r') as f:
				idiomas.add(f.read())
		idiomas = list(idiomas)
		# Metadatos de salida
		with self.output()['langs'].open('w') as f:
			f.write('\n'.join(idiomas))
	


# Generar diccionario
class GenerateDictionary(luigi.Task):
	"""docstring for CleanText"""
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	model_dir = luigi.Parameter()
	# ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	lang_file = luigi.Parameter(default='idiomas.tm') # Solo para tener el registro
	languages = luigi.Parameter()
	min_docs_per_lang = luigi.IntParameter(default=1)
	
	def requires(self):
		return SortByLanguage(self.pdf_dir,
							  self.txt_dir,
							  self.meta_file,
							  self.lang_file)

	def output(self):
		idiomas_permitidos = ['spanish','english','french','italian','german']
		idiomas = [i for i in self.languages.split(',') if i in idiomas_permitidos]
		return {idioma:luigi.LocalTarget(self.model_dir + '/diccionario_' + idioma + '.dict') for idioma in idiomas}
		# return luigi.LocalTarget(self.txt_dir + '/idiomas.txt')

	def run(self):
		print 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
		print 'GenerateDictionary'
		print self.languages #.split(',')

		# idiomas_permitidos = ['spanish','english','french','italian','german']
		# idiomas = [i for i in self.languages.split(',') if i in idiomas_permitidos]

		# Generar diccionario por idioma
		for idioma in self.output().keys():
			print '=========================='
			print 'Generando diccionario de ' + idioma

			rutaTextos = os.path.join(self.txt_dir,idioma)
			if os.path.exists(rutaTextos):
				ndocs = len(os.listdir(rutaTextos)) 
			else:
				ndocs = 0
			if ndocs < self.min_docs_per_lang:
				print "No hay suficientes muestras para generar el modelo. Omitiendo idioma" + idioma
				continue
			elif not os.path.exists(self.model_dir):
				print "Creando carpeta base para modelos."
				os.makedirs(self.model_dir)
			generarDiccionario(rutaTextos, self.model_dir, 6, idioma)
			#generarCorpus(rutaTextos, self.model_dir, 6, idioma)



# Corpus
class GenerateCorpus(luigi.Task):
	"""docstring for CleanText"""
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	model_dir = luigi.Parameter()
	# ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	lang_file = luigi.Parameter(default='idiomas.tm')
	languages = luigi.Parameter()
	min_docs_per_lang = luigi.IntParameter(default=1)

	def requires(self):
		return GenerateDictionary(self.pdf_dir,
							  	  self.txt_dir,
							  	  self.model_dir,
							  	  self.meta_file,
							  	  self.lang_file,
							      self.languages,
							      self.min_docs_per_lang)

	def output(self):
		return {idioma:luigi.LocalTarget(self.model_dir + '/corpus_' + idioma + '.mm') for idioma in self.input().iterkeys()}

	def run(self):
		# idiomas_permitidos = ['spanish','english','french','italian','german']
		# idiomas = [i for i in self.languages.split(',') if i in idiomas_permitidos]
		# Generar corpus por idioma
		for idioma in self.input().iterkeys():
			print '=========================='
			print 'Generando corpus de ' + idioma
			rutaTextos = os.path.join(self.txt_dir,idioma)
			generarCorpus(rutaTextos, self.model_dir, 6, idioma)


# LDA
from gensim import corpora
from gensim.models.ldamodel import LdaModel
import pickle

class TrainLDA(luigi.Task):
	"""Necesita corpus limpio por 
	idioma sin las stopwords
	viene del proceso de VECTORIZE"""
	# date_interval = luigi.DateIntervalParameter()
	n_topics = luigi.IntParameter(default=30) #numero de topicos
	chunk_size = luigi.IntParameter(default=100)
	update_e = luigi.IntParameter(default = 0)
	n_passes = luigi.IntParameter(default=10) #numero de pasadas al corpus
	# input_dir = luigi.Parameter()
	# clean_dir = luigi.Parameter()
	# model_dir = luigi.Parameter()

	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	model_dir = luigi.Parameter()
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	lang_file = luigi.Parameter(default='idiomas.tm')
	languages = luigi.Parameter()
	min_docs_per_lang = luigi.IntParameter(default=1)


	def requires(self):
		return {'dict':GenerateDictionary(self.pdf_dir,
							  	  self.txt_dir,
							  	  self.model_dir,
							  	  self.meta_file,
							  	  self.lang_file,
							      self.languages,
							      self.min_docs_per_lang),
				'corp':GenerateCorpus(self.pdf_dir,
							  	  self.txt_dir,
							  	  self.model_dir,
							  	  self.meta_file,
							  	  self.lang_file,
							      self.languages,
							      self.min_docs_per_lang)}

	def output(self):
		return {idioma:luigi.LocalTarget(self.model_dir + '/' + 'lda-%s-%d.lda' % (idioma, self.n_topics)) for idioma in self.input()['corp'].iterkeys()}
		# return luigi.LocalTarget(self.model_dir + '/' + 'lda-%s-%d.pickle' % (self.date_interval, self.n_topics))

	def run(self):

		# for d, c in zip(input()['dict'], input()['corp'])
		for idioma in self.input()['corp'].iterkeys():
			print '=============================='
			print os.path.join(self.model_dir,'diccionario_'+idioma+'.dict')
			print os.path.join(self.model_dir,'corpus_'+idioma+'.mm')
			print '=============================='
			dicc_path = os.path.join(self.model_dir,'diccionario_'+idioma+'.dict')
			corp_path = os.path.join(self.model_dir,'corpus_'+idioma+'.mm')
			dicc = corpora.Dictionary.load(dicc_path)
			corpus = corpora.MmCorpus(corp_path)
			if len(corpus) >= 1000:
				lda = LdaModel(corpus, id2word=dicc, num_topics=self.n_topics, update_every=self.update_e, chunksize=self.chunk_size, passes=self.n_passes)
			else:  
				lda = LdaModel(corpus, id2word=dicc, num_topics=self.n_topics)
			lda.save(self.output()[idioma].path)
				
	

if __name__ == '__main__':
	luigi.run()











