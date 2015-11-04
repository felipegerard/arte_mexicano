# coding=utf-8

import luigi
import os
import sys
import inspect
import re
import pickle
import unicodedata

from gensim import corpora
from dictionaries import generarDiccionario
from gencorp import generarCorpus
from text_basic import DetectLanguages

# Generate dictionary for each language and cleanliness level
class GenerateDictionary(luigi.Task):
	'''Genera un diccionario por idioma'''
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	# jpg_dir = luigi.Parameter()
	# image_meta_dir = luigi.Parameter()
	model_dir = luigi.Parameter()		# Carpeta donde se guardan los modelos
	meta_dir = luigi.Parameter(default='meta')
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	lang_file = luigi.Parameter(default='idiomas.tm')	# Solo para tener el registro
	clean_level = luigi.Parameter(default='stopwords')
	languages = luigi.Parameter()						# Idiomas a procesar
	max_word_length = luigi.IntParameter(default=6)		# Máxima longitud de las palabras. Palabras más largas se truncan
	min_docs_per_lang = luigi.IntParameter(default=1)	# Mínimo número de documentos por idioma para procesar el idioma
	
	def requires(self):
		if self.clean_level == 'raw':
			flags = 'raw'
		elif self.clean_level == 'clean':
			flags = 'raw,clean'
		elif self.clean_level == 'stopwords':
			flags = 'raw,clean,stopwords'
		else:
			print 'WARNING: No valid clean level given. Defaulting to stopword format...'
			flags = 'raw,clean,stopwords'

		return DetectLanguages(pdf_dir=self.pdf_dir,
							  txt_dir=self.txt_dir,
							  # jpg_dir = self.jpg_dir,
							  # image_meta_dir = self.image_meta_dir,
							  meta_dir=self.meta_dir,
							  meta_file=self.meta_file,
							  lang_file=self.lang_file,
							  clean_level=flags)

	def output(self):
		idiomas_permitidos = ['spanish','english','french','italian','german'] # Idiomas fuera de esta lista no se procesan
		idiomas = self.languages.split(',')
		idiomas = [i for i in idiomas if i in idiomas_permitidos]
		if self.clean_level in ('raw','clean','stopwords'):
			kind = self.clean_level
		else:
			kind = 'stopwords'
		output = {
					'langs':
					{
						idioma:luigi.LocalTarget(self.model_dir + '/diccionario_' + kind + '_' + idioma + '.dict')
						for idioma in idiomas
					},
					'files':self.input()['files']
				}
		return output

	def run(self):
		print 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
		print 'GenerateDictionary'
		print self.languages #.split(',')

		if self.clean_level in ('raw','clean','stopwords'):
			kind = self.clean_level
		else:
			kind = 'stopwords'

		# Generar diccionario por idioma
		for idioma in self.output()['langs'].keys():
			print '=========================='
			print 'Generando diccionario de ' + idioma

			# Obtener rutas de textos por idioma y nivel de limpieza
			rutaTextos = os.path.join(self.txt_dir,kind,idioma)
			print rutaTextos
			if os.path.exists(rutaTextos):
				ndocs = len(os.listdir(rutaTextos)) 
			else:
				ndocs = 0

			# Crear carpeta de modelos si no existen
			if ndocs < self.min_docs_per_lang:
				print "No hay suficientes muestras para generar el modelo. Omitiendo idioma" + idioma
				continue
			elif not os.path.exists(self.model_dir):
				print "Creando carpeta base para modelos."
				os.makedirs(self.model_dir)

			# Generar el diccionario
			nombre_diccionario = self.output()['langs'][idioma].path
			print rutaTextos
			diccionario = generarDiccionario(rutaTextos, min_doc_freq=0, truncamiento=self.max_word_length)
			pprint(diccionario.token2id)
			diccionario.save(nombre_diccionario)
			


# Generate corpus for each language and cleanliness level
class GenerateCorpus(luigi.Task):
	'''Genera un corpus por idioma'''
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
		return GenerateDictionary(pdf_dir=self.pdf_dir,
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

	def output(self):
		if self.clean_level in ('raw','clean','stopwords'):
			kind = self.clean_level
		else:
			kind = 'stopwords'
		return {
					'langs':
					{
						idioma:luigi.LocalTarget(self.model_dir + '/corpus_' + kind + '_' + idioma + '.mm')
						for idioma in self.input()['langs'].iterkeys()
					},
					'files':self.input()['files']
				}

	def run(self):
		if self.clean_level in ('raw','clean','stopwords'):
			kind = self.clean_level
		else:
			kind = 'stopwords'

		# Generar corpus por idioma
		for idioma in self.input()['langs'].iterkeys():
			print '=========================='
			print 'Generando corpus de ' + idioma
			rutaTextos = os.path.join(self.txt_dir,kind,idioma)
			
			# Generar el corpus
			ruta_corpus = self.output()['langs'][idioma].path
			ruta_diccionario = self.input()['langs'][idioma].path
			corpus = generarCorpus(ruta_diccionario, rutaTextos, truncamiento=self.max_word_length)
			corpora.MmCorpus.serialize(ruta_corpus, corpus)