# coding=utf-8

import luigi
import os
import sys
import inspect
import re
import pickle
import unicodedata

from gensim import corpora
from gensim.models.ldamodel import LdaModel

from dict_corp import GenerateDictionary, GenerateCorpus


# Train LDA models
class TrainLDA(luigi.Task):
	'''Entrena varios modelos LDA que luego serán analizados'''
	# Parámetros LDA
	topic_range = luigi.Parameter(default='30,31,1')	# Número de topicos. Debe ser una lista de tres números, separados por comas, como las entradas de la función 'range'. Por ejemplo, si se quiere 200 tópicos, '200,201,1'. Si se quiere 10, 15 y 20, '10,21,5', etc

	# Parámetros LDA por pedazos
	by_chunks = luigi.BoolParameter(default=False)		# Hacer LDA por pedazos?
	chunk_size = luigi.IntParameter(default=100)		# Tamaño de los pedazos
	update_e = luigi.IntParameter(default = 0)			# Cada cuánto actualizar?
	n_passes = luigi.IntParameter(default=10) 			# Número de pasadas al corpus
	
	# Parámetros corpus y diccionario
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	# jpg_dir = luigi.Parameter()
	# image_meta_dir = luigi.Parameter()
	model_dir = luigi.Parameter()
	meta_dir = luigi.Parameter(default='meta')
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	lang_file = luigi.Parameter(default='idiomas.tm')
	clean_level = luigi.Parameter(default='stopwords')
	languages = luigi.Parameter()
	max_word_length = luigi.IntParameter(default=6)
	min_docs_per_lang = luigi.IntParameter(default=1)


	def requires(self):
		return {
					'dict':GenerateDictionary(pdf_dir=self.pdf_dir,
											  txt_dir=self.txt_dir,
											  # jpg_dir = self.jpg_dir,
											  # image_meta_dir = self.image_meta_dir,	
											  model_dir=self.model_dir,
											  meta_dir=self.meta_dir,
											  meta_file=self.meta_file,
											  lang_file=self.lang_file,
											  clean_level=self.clean_level,
											  languages=self.languages,
											  max_word_length=self.max_word_length,
											  min_docs_per_lang=self.min_docs_per_lang),
					'corp':GenerateCorpus(pdf_dir=self.pdf_dir,
										  txt_dir=self.txt_dir,
										  # jpg_dir = self.jpg_dir,
										  # image_meta_dir = self.image_meta_dir,
										  model_dir=self.model_dir,
										  meta_dir=self.meta_dir,
										  meta_file=self.meta_file,
										  lang_file=self.lang_file,
										  clean_level=self.clean_level,
										  languages=self.languages,
										  max_word_length=self.max_word_length,
										  min_docs_per_lang=self.min_docs_per_lang)
				}

	def output(self):
		topic_range = self.topic_range.split(',')
		topic_range = [int(i) for i in topic_range]
		topic_range = range(topic_range[0],topic_range[1],topic_range[2])

		if self.clean_level in ('raw','clean','stopwords'):
			kind = self.clean_level
		else:
			kind = 'stopwords'

		return {
					'langs':{
							idioma:
								{
									n_topics:luigi.LocalTarget(self.model_dir + '/' + 'lda-%s-%s-%d.lda' % (kind, idioma, n_topics))
									for n_topics in topic_range
								}
							for idioma in self.input()['corp']['langs'].iterkeys()
						},
					'files':self.input()['corp']['files']
				}

	def run(self):
		if self.clean_level in ('raw','clean','stopwords'):
			kind = self.clean_level
		else:
			kind = 'stopwords'

		for idioma in self.output()['langs'].iterkeys():
			dicc_path = self.input()['dict']['langs'][idioma].path
			corp_path = self.input()['corp']['langs'][idioma].path
			print '=============================='
			print 'Corriendo LDA de %s con nivel de limpieza %s' % (idioma, kind)
			print '=============================='

			# Cargar diccionario y corpus
			dicc = corpora.Dictionary.load(dicc_path)
			corpus = corpora.MmCorpus(corp_path)

			# Correr LDA del idioma para cada numero de topicos
			for n_topics in self.output()['langs'][idioma].iterkeys():
				print 'Número de tópicos: ' + str(n_topics)
				if self.by_chunks:
					lda = LdaModel(corpus, id2word=dicc, num_topics=n_topics, update_every=self.update_e, chunksize=self.chunk_size, passes=self.n_passes)
				else:
					lda = LdaModel(corpus, id2word=dicc, num_topics=n_topics, passes=1)
				lda.save(self.output()['langs'][idioma][n_topics].path)


# Classify texts according to trained LDA models
class PredictLDA(luigi.Task):
	'''Usa un modelo de LDA para clasificar los libros'''
	# Variables de predictLDA
	res_dir = luigi.Parameter() # Carpeta para guardar archivos de clasificaciones

	# Variables de LDA
	topic_range = luigi.Parameter(default='30,31,1')
	by_chunks = luigi.BoolParameter(default=False)
	chunk_size = luigi.IntParameter(default=100)
	update_e = luigi.IntParameter(default = 0)
	n_passes = luigi.IntParameter(default=10)

	# Variables de corpus
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	# jpg_dir = luigi.Parameter()
	# image_meta_dir = luigi.Parameter()
	model_dir = luigi.Parameter()
	meta_dir = luigi.Parameter(default='meta')
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	lang_file = luigi.Parameter(default='idiomas.tm') # Solo para tener el registro
	clean_level = luigi.Parameter(default='stopwords')
	languages = luigi.Parameter()
	max_word_length = luigi.IntParameter(default=6)
	min_docs_per_lang = luigi.IntParameter(default=1)

	def requires(self):
		return {
			'lda':TrainLDA(topic_range=self.topic_range,
							by_chunks=self.by_chunks,
							chunk_size=self.chunk_size,
							update_e=self.update_e,
							n_passes=self.n_passes,
							pdf_dir=self.pdf_dir,
							txt_dir=self.txt_dir,
							# jpg_dir = self.jpg_dir,
							# image_meta_dir = self.image_meta_dir,
							model_dir=self.model_dir,
							meta_dir=self.meta_dir,
							meta_file=self.meta_file,
							lang_file=self.lang_file,
							clean_level=self.clean_level,
							languages=self.languages,
							max_word_length=self.max_word_length,
							min_docs_per_lang=self.min_docs_per_lang),

				'corp':GenerateCorpus(pdf_dir=self.pdf_dir,
									  txt_dir=self.txt_dir,
									  # jpg_dir = self.jpg_dir,
									  # image_meta_dir = self.image_meta_dir,
									  model_dir=self.model_dir,
									  meta_dir=self.meta_dir,
									  meta_file=self.meta_file,
									  lang_file=self.lang_file,
									  clean_level=self.clean_level,
									  languages=self.languages,
									  max_word_length=self.max_word_length,
									  min_docs_per_lang=self.min_docs_per_lang)
			}

	def output(self):
		topic_range = self.topic_range.split(',')
		topic_range = [int(i) for i in topic_range]
		topic_range = range(topic_range[0],topic_range[1],topic_range[2])
		if self.clean_level in ('raw','clean','stopwords'):
			kind = self.clean_level
		else:
			kind = 'stopwords'
		
		return {
					'langs':
					{
						idioma:
						{
							n_topics:
							{
								"doc_topics" : luigi.LocalTarget(os.path.join(self.res_dir, 'topic_results_%s_%s_%d.pickle' % (kind, idioma, n_topics))),
								"topics" : luigi.LocalTarget(os.path.join(self.res_dir, 'topics_%s_%s_%d.pickle' % (kind, idioma, n_topics)))
							}
							for n_topics in topic_range
						}
						for idioma in self.input()['corp']['langs'].iterkeys()
					},
					'files':self.input()['corp']['files']
				}


	def run(self):
		if self.clean_level in ('raw','clean','stopwords'):
			kind = self.clean_level
		else:
			kind = 'stopwords'

		if not os.path.exists(self.res_dir):
			print 'Creando carpeta para resultados...'
			os.mkdir(self.res_dir)

		# Aplicar cada modelo
		for idioma, modelos in self.input()['lda']['langs'].iteritems():
			corp_path = self.input()['corp']['langs'][idioma].path
			corpus = corpora.MmCorpus(corp_path)
			for n_topics, modelo in modelos.iteritems():
				model_path = modelo.path
				model = LdaModel.load(model_path)
				classification = []
				for doc in corpus:
					topic = model.get_document_topics(doc)
					classification.append(topic)
				print '--------------------------------------'
				print 'USER INFO: Clasificando textos en %s con nivel de limpieza "%s" con %d tópicos' % (idioma, kind, n_topics)
				model.print_topics(len(corpus),5)
				with self.output()['langs'][idioma][n_topics]['doc_topics'].open('w') as f:
					pickle.dump(classification, f)
				with self.output()['langs'][idioma][n_topics]['topics'].open('w') as f:
					pickle.dump(model.print_topics(n_topics,5), f) # el 5 es un parámetro que se puede editar (numero de palabras del tópico a mostrar)	

# Generar salidas de LDA para que lo cheque una persona
