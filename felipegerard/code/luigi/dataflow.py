
# coding=utf-8
## ES IMPORTANTE INDICAR EL ENCODING

import luigi
import os
import sys
import inspect
import re
import pickle
import unicodedata
#from gensim import corpora, models, similarities

import shutil
from pprint import pprint

from gensim import corpora
from gensim.similarities import Similarity
from gensim.models.ldamodel import LdaModel

sys.path.append('functions')
sys.path.append('jared')
sys.path.append('lechuga')

#from GeneradorDiccionario import GeneradorDiccionario
from dictionaries import generarDiccionario
from GeneradorCorpus import GeneradorCorpus
from GeneradorLSI import GeneradorLSI
from helper_functions import *

from data_flow_jared_modif import *

#from ShowLDA_comment import *


# ----------------------------------------------------------------
# Data Flow


# Input PDF directory
class InputPDF(luigi.ExternalTask):
	filename = luigi.Parameter()
	def output(self):
		return luigi.LocalTarget(self.filename)

# Extract raw text
class ReadText(luigi.Task):
	'''Extraer texto de los PDFs de un libro,
	pegarlos en un solo archivo en formato crudo
	y guardar el resultado'''
	book_name = luigi.Parameter()		# Nombre del libro
	pdf_dir = luigi.Parameter() 		# Carpeta de PDFs
	txt_dir = luigi.Parameter()			# Carpeta de textos
	jpg_dir = luigi.Parameter()			# Carpeta de JPGs
	image_meta_dir = luigi.Parameter()	# Carpeta con archivos de metadatos para definir qué archivos son imágenes
	meta_dir = luigi.Parameter(default='meta')	# Nombre del archivo de metadatos
	meta_file = luigi.Parameter(default='librosAgregados.tm') # Nombre del archivo de metadatos libro-idioma

	def requires(self):
		pdf_bookdir = os.path.join(self.pdf_dir, self.book_name)
		return {
					'pdf':InputPDF(pdf_bookdir),
					'images':IdentificarImagenes(self.book_name,self.jpg_dir,self.image_meta_dir)
				}

	def output(self):
		return luigi.LocalTarget(os.path.join(self.txt_dir,self.meta_dir,self.book_name+'.meta'))
		
	def run(self):
		# Extraer textos
		with self.input()['images'].open('r') as f:
			lista_negra = f.read().split('\n')
			lista_negra = [i + '.pdf' for i in lista_negra]
		#rutaVolumenes = obtenerRutaVolumenes(inputPDF.path)
		ruta_pdfs = self.input()['pdf'].path
		lista_pdfs = [x for x in os.listdir(ruta_pdfs) if ".pdf" in x]
		rutaVolumenes = [os.path.join(ruta_pdfs,i) for i in lista_pdfs if i not in lista_negra]
		pprint(lista_negra)
		pprint(lista_pdfs)
		pprint(rutaVolumenes)
		contenido = convertirVolumenes(rutaVolumenes)
		idioma = detectarIdioma(contenido)
		lang_path = os.path.join(self.txt_dir,idioma)
		save_content(lang_path, self.book_name, contenido)

		# Guardar los metadatos
		with self.output().open('w') as f:
			f.write(idioma)
		guardarMetadatos(self.book_name,idioma,
			os.path.join(self.txt_dir),self.meta_file)

# Clean text
class CleanText(luigi.Task):
	'''Limpiar el texto de un libro según el nivel de limpieza deseado
	y guardarlo en su carpeta correspondiente'''
	book_name = luigi.Parameter()
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	jpg_dir = luigi.Parameter()
	image_meta_dir = luigi.Parameter()
	meta_dir = luigi.Parameter(default='meta')
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	clean_level = luigi.Parameter(default='raw,clean,stopwords') # Nivel de limpieza. Cualquier combinación de 'raw', 'clean' y 'stopwords', separados por comas

	def requires(self):
		return ReadText(book_name = self.book_name,
						pdf_dir = self.pdf_dir,
						txt_dir = os.path.join(self.txt_dir, 'raw'),
						jpg_dir = self.jpg_dir,
						image_meta_dir = self.image_meta_dir,
						meta_dir = self.meta_dir,
						meta_file = self.meta_file)

	def output(self):
		flags = self.clean_level.split(',')
		if not ('raw' in flags or 'clean' in flags):
			print 'WARNING: No cleaning flags defined. Defaulting to raw format only...'
			flags = ['raw']
		metafiles = {kind:os.path.join(self.txt_dir,kind,'meta',self.book_name+'.meta')
					for kind in flags}
		return {kind:luigi.LocalTarget(path)
				for kind, path in metafiles.iteritems()}
		
	def run(self):
		flags = self.output().keys()
		if flags == ['raw']:
			print 'No hacemos limpieza de %s' % (self.book_name)

		# Leemos el idioma de los metadatos
		with self.input().open('r') as f:
			idioma = f.read()
		if 'clean' in flags:
			# Leemos el contenido crudo
			with open(os.path.join(self.txt_dir,'raw',idioma,self.book_name+'.txt'), 'r') as f:
				contenido = f.read()
			contenido = clean_text(contenido)
			lang_path = os.path.join(self.txt_dir,'clean',idioma)
			save_content(lang_path, self.book_name, contenido)
			if 'stopwords' in flags:
				contenido = remove_stopwords(contenido, idioma)
				lang_path = os.path.join(self.txt_dir,'stopwords',idioma)
				save_content(lang_path, self.book_name, contenido)
		elif 'stopwords' in flags:
			print 'WARNING: Cannot remove stopwords without cleaning first. Ommiting "stopwords" flag.'
		
		# Guardar los metadatos
		for kind, o in self.output().iteritems():
			with o.open('w') as f:
				f.write(idioma)
			guardarMetadatos(self.book_name,idioma,
				os.path.join(self.txt_dir,kind),self.meta_file)
	

# Detect languages and write language metadata. Possibly obsolete
class DetectLanguages(luigi.Task):
	'''Detectar idiomas de los libros y escribir archivo
	con los nombres de todos los idiomas detectados'''
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	jpg_dir = luigi.Parameter()
	image_meta_dir = luigi.Parameter()
	meta_dir = luigi.Parameter(default='meta')
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	lang_file = luigi.Parameter(default='idiomas.tm')
	clean_level = luigi.Parameter(default='raw,clean,stopwords')

	def requires(self):
		return [CleanText(book_name=book_name,
						  pdf_dir=self.pdf_dir,
						  txt_dir=self.txt_dir,
						  jpg_dir = self.jpg_dir,
						  image_meta_dir = self.image_meta_dir,
						  meta_dir=self.meta_dir,
						  meta_file=self.meta_file,
						  clean_level=self.clean_level)
				for book_name in os.listdir(self.pdf_dir)]

	def output(self):
		flags = self.input()[0].keys()
		metapath = os.path.join(self.txt_dir,self.lang_file)
		return {
					'langs':{
						kind:luigi.LocalTarget(os.path.join(self.txt_dir,kind,self.lang_file))
						for kind in flags
					},
					'files':self.input()
				}
		
	def run(self):
		for kind, target in self.output()['langs'].iteritems():
			idiomas = set()
			txt_kind_meta_dir = os.path.join(self.txt_dir,kind,self.meta_dir)
			for p in os.listdir(txt_kind_meta_dir):
				p = os.path.join(txt_kind_meta_dir, p)
				with open(p, 'r') as f:
					idiomas.add(f.read())
			idiomas = list(idiomas)
			# Metadatos de salida
			with target.open('w') as f:
				f.write('\n'.join(idiomas))
	

# Generate dictionary for each language and cleanliness level
class GenerateDictionary(luigi.Task):
	'''Genera un diccionario por idioma'''
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	jpg_dir = luigi.Parameter()
	image_meta_dir = luigi.Parameter()
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
							  jpg_dir = self.jpg_dir,
							  image_meta_dir = self.image_meta_dir,
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
			diccionario.save(nombre_diccionario)
			


# Generate corpus for each language and cleanliness level
class GenerateCorpus(luigi.Task):
	'''Genera un corpus por idioma'''
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	jpg_dir = luigi.Parameter()
	image_meta_dir = luigi.Parameter()
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
								  jpg_dir = self.jpg_dir,
								  image_meta_dir = self.image_meta_dir,
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
			nombre_corpus = self.output()['langs'][idioma].path
			ruta_diccionario = self.input()['langs'][idioma].path
			generadorCorpus = GeneradorCorpus(rutaTextos, ruta_diccionario, self.max_word_length)
			generadorCorpus.obtenerLibros()
			generadorCorpus.generarCorpus()
			generadorCorpus.serializarCorpus(nombre_corpus)


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
	jpg_dir = luigi.Parameter()
	image_meta_dir = luigi.Parameter()
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
											  jpg_dir = self.jpg_dir,
											  image_meta_dir = self.image_meta_dir,	
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
										  jpg_dir = self.jpg_dir,
										  image_meta_dir = self.image_meta_dir,
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
	jpg_dir = luigi.Parameter()
	image_meta_dir = luigi.Parameter()
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
							jpg_dir = self.jpg_dir,
							image_meta_dir = self.image_meta_dir,
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
									  jpg_dir = self.jpg_dir,
									  image_meta_dir = self.image_meta_dir,
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

# Modelo LSI (TF-IDF + SVD)
class TrainLSI(luigi.Task):
	'''Entrena modelos LSI para varios números de tópicos'''

	# Parámetros LSI
	topic_range = luigi.Parameter(default='30,31,1') # Número de topicos. Debe ser una lista de tres números, separados por comas, como las entradas de la función 'range'. Por ejemplo, si se quiere 200 tópicos, '200,201,1'. Si se quiere 10, 15 y 20, '10,21,5', etc
	
	# Parámetros de corpus
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	jpg_dir = luigi.Parameter()
	image_meta_dir = luigi.Parameter()
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
					'dict':GenerateDictionary(pdf_dir=self.pdf_dir,
											  txt_dir=self.txt_dir,
											  jpg_dir = self.jpg_dir,
											  image_meta_dir = self.image_meta_dir,
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
										  jpg_dir = self.jpg_dir,
										  image_meta_dir = self.image_meta_dir,
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
								'tfidf':luigi.LocalTarget(self.model_dir + '/' + 'model-%s-%s-%d.tfidf' % (kind, idioma, n_topics)),
								'lsi-model':luigi.LocalTarget(self.model_dir + '/' + 'model-%s-%s-%d.lsi' % (kind, idioma, n_topics)),
								'lsi-index':luigi.LocalTarget(self.model_dir + '/' + 'model-%s-%s-%d.lsi.index' % (kind, idioma, n_topics))
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

		for idioma, salida in self.output()['langs'].iteritems():
			print '=============================='
			print 'Corriendo LSI de %s con nivel de limpieza %s' % (idioma, kind)
			print '=============================='

			# Cargar diccionario y corpus
			generadorLSI = GeneradorLSI(ruta_diccionario=self.input()['dict']['langs'][idioma].path,
										ruta_corpus = self.input()['corp']['langs'][idioma].path,
										ruta_modelo_tfidf = 'dummy',
										ruta_modelo_lsi = 'dummy',
										ruta_indice = 'dummy',
										temas = 0)

			# Correr LSI del idioma para cada numero de topicos.
			# ESTO SE PUEDE MEJORAR PARA CARGAR SOLO UNA VEZ EL DICCIONARIO Y EL CORPUS DE UN IDIOMA
			for n_topics, o in salida.iteritems():
				print 'Número de tópicos: ' + str(n_topics)
				# Parámetros para el número de tópicos
				generadorLSI.ruta_modelo_tfidf = o['tfidf'].path
				generadorLSI.ruta_modelo_lsi = o['lsi-model'].path
				generadorLSI.ruta_indice = o['lsi-index'].path
				generadorLSI.temas = n_topics
				generadorLSI.cargarDiccionarioYCorpus()
				# Correr el modelo
				generadorLSI.generarYSerializarTfIdf()
				generadorLSI.generarYSerializarLSIModel()
				generadorLSI.generarYSerializarIndice()


# Calcular similitudes de LSI
class GroupByLSI(luigi.Task):
	''''''

	# Parámetros GroupByLSI
	res_dir = luigi.Parameter() # Carpeta para guardar archivos de clasificaciones
	num_similar_docs = luigi.IntParameter(default=5)
	
	# Parámetros TrainLSI
	topic_range = luigi.Parameter(default='30,31,1') #numero de topicos
	
	# Parámetros corpus
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	jpg_dir = luigi.Parameter()
	image_meta_dir = luigi.Parameter()
	model_dir = luigi.Parameter()
	meta_dir = luigi.Parameter(default='meta')
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	lang_file = luigi.Parameter(default='idiomas.tm') # Solo para tener el registro
	clean_level = luigi.Parameter(default='stopwords')
	languages = luigi.Parameter()
	max_word_length = luigi.IntParameter(default=6)
	min_docs_per_lang = luigi.IntParameter(default=1)


	def requires(self):
		return TrainLSI(topic_range=self.topic_range,
						pdf_dir=self.pdf_dir,
						txt_dir=self.txt_dir,
						jpg_dir = self.jpg_dir,
						image_meta_dir = self.image_meta_dir,
						model_dir=self.model_dir,
						meta_dir=self.meta_dir,
						meta_file=self.meta_file,
						lang_file=self.lang_file,
						clean_level=self.clean_level,
						languages=self.languages,
						max_word_length=self.max_word_length,
						min_docs_per_lang=self.min_docs_per_lang)

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
							n_topics:luigi.LocalTarget(self.res_dir + '/' + 'lsi-results-%s-%s-%d.tsv' % (kind, idioma, n_topics))
							for n_topics in topic_range
						}
						for idioma in self.input()['langs'].iterkeys()
					},
					'files':self.input()['files']
				}

	def run(self):
		if self.clean_level in ('raw','clean','stopwords'):
			kind = self.clean_level
		else:
			kind = 'stopwords'

		# Guardamos las similitudes en un archivo con un formato sencillo
		# NOTA: EL ÍNDICE YA DE POR SÍ GUARDA LAS SIMILITUDES. NO ES NECESARIO CALCULARLAS DE NUEVO
		for idioma, salida in self.output()['langs'].iteritems():
			file_list = os.listdir(os.path.join(self.txt_dir,kind,idioma))
			for n_topics, o in salida.iteritems():
				index = Similarity.load(self.input()['langs'][idioma][n_topics]['lsi-index'].path)
				sims = arrange_similarities(index, file_list, num_sims=self.num_similar_docs)
				sims = '\n'.join(['\t'.join([str(i) for i in t]) for t in sims])
				with o.open('w') as f:
					f.write(sims)
				



if __name__ == '__main__':
	luigi.run()











