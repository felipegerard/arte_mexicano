
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
	clean_level = luigi.Parameter(default='raw,clean,stopwords')

	def requires(self):
		pdf_bookdir = os.path.join(self.pdf_dir, self.book_name)
		return InputPDF(pdf_bookdir)

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
		# Extraer textos
		idioma, contenido = extraerVolumen(self.input())

		flags = self.output().keys()
		if 'raw' in flags:
			lang_path = os.path.join(self.txt_dir,'raw',idioma)
			save_content(lang_path, self.book_name, contenido)

		if 'clean' in flags:
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
	

# Meter a carpetas de idioma. Si no hacemos esto entonces no es idempotente
class DetectLanguages(luigi.Task):
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	meta_dir = luigi.Parameter(default='meta')
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	lang_file = luigi.Parameter(default='idiomas.tm')
	clean_level = luigi.Parameter(default='raw,clean,stopwords')

	def requires(self):
		return [ReadText(book_name, self.pdf_dir, self.txt_dir, self.meta_dir, self.meta_file, self.clean_level)
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
	

# Generar diccionario
class GenerateDictionary(luigi.Task):
	"""docstring for CleanText"""
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	model_dir = luigi.Parameter()
	# ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')
	meta_dir = luigi.Parameter(default='meta')
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	lang_file = luigi.Parameter(default='idiomas.tm') # Solo para tener el registro
	clean_level = luigi.Parameter(default='stopwords')
	languages = luigi.Parameter()
	min_docs_per_lang = luigi.IntParameter(default=1)
	
	def requires(self):
		if self.clean_level == 'raw':
			flags = 'raw'
		elif self.clean_level == 'clean':
			flags = 'raw,clean'
		elif self.clean_level == 'stopwords':
			flags = 'raw,clean,stopwords'
		else:
			print 'WARNING: No valid clean level given. Defaulting to stopword format...'
			self.clean_level = 'stopwords'
			flags = 'raw,clean,stopwords'

		return {
					'clean_level':self.clean_level,
					'detect':DetectLanguages(self.pdf_dir,
											  self.txt_dir,
											  self.meta_dir,
											  self.meta_file,
											  self.lang_file,
											  flags)
				}

	def output(self):
		idiomas_permitidos = ['spanish','english','french','italian','german']
		idiomas = self.languages.split(',')
		idiomas = [i for i in idiomas if i in idiomas_permitidos]
		output = {
					'langs':{
						idioma:luigi.LocalTarget(self.model_dir + '/diccionario_' + self.input()['clean_level'] + '_' + idioma + '.dict')
						for idioma in idiomas
					},
				'files':self.input()['files']}
		return output
		# return luigi.LocalTarget(self.txt_dir + '/idiomas.txt')

	def run(self):
		print 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
		print 'GenerateDictionary'
		print self.languages #.split(',')

		# Generar diccionario por idioma
		for idioma in self.output()['langs'].keys():
			print '=========================='
			print 'Generando diccionario de ' + idioma

			rutaTextos = os.path.join(self.txt_dir,self.input()['clean_level'],idioma)
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
			nombre_diccionario = self.output()['langs'][idioma].path
			generadorDiccionario = GeneradorDiccionario(carpeta_textos, truncamiento)
			generadorDiccionario.generarDiccionario()
			generadorDiccionario.serializarDiccionario(nombre_diccionario)
			#generarDiccionario(rutaTextos, self.model_dir, 6, idioma)
			


# Corpus
class GenerateCorpus(luigi.Task):
	"""docstring for CleanText"""
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	model_dir = luigi.Parameter()
	# ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')
	meta_dir = luigi.Parameter(default='meta')
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	lang_file = luigi.Parameter(default='idiomas.tm')
	languages = luigi.Parameter()
	min_docs_per_lang = luigi.IntParameter(default=1)

	def requires(self):
		return GenerateDictionary(self.pdf_dir,
							  	  self.txt_dir,
							  	  self.model_dir,
							  	  self.meta_dir,
							  	  self.meta_file,
							  	  self.lang_file,
							      self.languages,
							      self.min_docs_per_lang)

	def output(self):
		return {'langs':{idioma:luigi.LocalTarget(self.model_dir + '/corpus_' + idioma + '.mm') for idioma in self.input()['langs'].iterkeys()},
				'files':self.input()['files']}

	def run(self):
		# Generar corpus por idioma
		for idioma in self.input()['langs'].iterkeys():
			print '=========================='
			print 'Generando corpus de ' + idioma
			rutaTextos = os.path.join(self.txt_dir,idioma)
			generarCorpus(rutaTextos, self.model_dir, 6, idioma)


# Entrenamiento LDA
from gensim import corpora
from gensim.models.ldamodel import LdaModel
import pickle

class TrainLDA(luigi.Task):
	"""Necesita corpus limpio por 
	idioma sin las stopwords
	viene del proceso de VECTORIZE"""
	# date_interval = luigi.DateIntervalParameter()
	topic_range = luigi.Parameter(default='30,31,1') #numero de topicos
	by_chunks = luigi.BoolParameter(default=False)
	chunk_size = luigi.IntParameter(default=100)
	update_e = luigi.IntParameter(default = 0)
	n_passes = luigi.IntParameter(default=10) #numero de pasadas al corpus
	
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	model_dir = luigi.Parameter()
	meta_dir = luigi.Parameter(default='meta')
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	lang_file = luigi.Parameter(default='idiomas.tm')
	languages = luigi.Parameter()
	min_docs_per_lang = luigi.IntParameter(default=1)


	def requires(self):
		return {'dict':GenerateDictionary(self.pdf_dir,
							  	  self.txt_dir,
							  	  self.model_dir,
							  	  self.meta_dir,
							  	  self.meta_file,
							  	  self.lang_file,
							      self.languages,
							      self.min_docs_per_lang),
				'corp':GenerateCorpus(self.pdf_dir,
							  	  self.txt_dir,
							  	  self.model_dir,
							  	  self.meta_dir,
							  	  self.meta_file,
							  	  self.lang_file,
							      self.languages,
							      self.min_docs_per_lang)}

	def output(self):
		topic_range = self.topic_range.split(',')
		topic_range = [int(i) for i in topic_range]
		topic_range = range(topic_range[0],topic_range[1],topic_range[2])
		return {
					'langs':{
							idioma:
								{
									n_topics:luigi.LocalTarget(self.model_dir + '/' + 'lda-%s-%d.lda' % (idioma, n_topics))
									for n_topics in topic_range
								}
							for idioma in self.input()['corp']['langs'].iterkeys()
						},
					'files':self.input()['corp']['files']
				}

	def run(self):
		for idioma in self.output()['langs'].iterkeys():
			dicc_path = self.input()['dict']['langs'][idioma].path
			corp_path = self.input()['corp']['langs'][idioma].path
			print '=============================='
			print 'Corriendo LDA de ' + idioma
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


class PredictLDA(luigi.Task):
	"""Necesita el modelo LDA"""
	#variables de predictLDA
	res_dir = luigi.Parameter()

	#variables de LDA
	topic_range = luigi.Parameter(default='30,31,1') #numero de topicos
	by_chunks = luigi.BoolParameter(default=False)
	chunk_size = luigi.IntParameter(default=100)
	update_e = luigi.IntParameter(default = 0)
	n_passes = luigi.IntParameter(default=10) #numero de pasadas al corpus

	#variables de corpus
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	model_dir = luigi.Parameter()
	meta_dir = luigi.Parameter(default='meta')
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	lang_file = luigi.Parameter(default='idiomas.tm')
	languages = luigi.Parameter()
	min_docs_per_lang = luigi.IntParameter(default=1)

	def requires(self):
	    return {'lda':TrainLDA(self.topic_range,
	                    self.by_chunks,
	                    self.chunk_size,
	                    self.update_e,
	                    self.n_passes,
	                    self.pdf_dir,
	                    self.txt_dir,
	                    self.model_dir,
	                    self.meta_dir,
	                    self.meta_file,
	                    self.lang_file,
	                    self.languages,
	                    self.min_docs_per_lang),
	        'corp':GenerateCorpus(self.pdf_dir,
	                    self.txt_dir,
	                    self.model_dir,
	                    self.meta_dir,
	                    self.meta_file,
	                    self.lang_file,
	                    self.languages,
	                    self.min_docs_per_lang)}

	def output(self):
	    # return {"doc_topics" : luigi.LocalTarget(os.path.join(self.res_dir, self.topic_results)),
	    #         "topics" : luigi.LocalTarget(os.path.join(self.res_dir, self.topics))
	    #         }
	    topic_range = self.topic_range.split(',')
	    topic_range = [int(i) for i in topic_range]
	    topic_range = range(topic_range[0],topic_range[1],topic_range[2])

	    return {
	            idioma:
	              {
	                n_topics:
	                  {
	                    "doc_topics" : luigi.LocalTarget(os.path.join(self.res_dir, 'topic_results_'+idioma+'_'+str(n_topics)+'.pickle')),
	                    "topics" : luigi.LocalTarget(os.path.join(self.res_dir, 'topics_'+idioma+'_'+str(n_topics)+'.pickle'))
	                  }
	                for n_topics in topic_range
	              }
	            for idioma in self.input()['corp']['langs'].iterkeys()
	          }

	def run(self):
	    if not os.path.exists(self.res_dir):
			print 'Creando carpeta para resultados NIGGANIGGANIGAGGAGA...'
			os.mkdir(self.res_dir)
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
        		print 'Clasificando textos en ' + idioma + ' con ' + str(n_topics) + ' tópicos'
		        with self.output()[idioma][n_topics]['doc_topics'].open('w') as f:
		        	pickle.dump(classification, f)
		        with self.output()[idioma][n_topics]['topics'].open('w') as f:
		        	pickle.dump(model.print_topics(len(corpus),5), f) # el 5 es un parámetro que se puede editar (numero de palabras del tópico a mostrar)	
		

if __name__ == '__main__':
	luigi.run()











