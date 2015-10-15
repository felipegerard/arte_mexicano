# coding=utf-8

import luigi
import os
import sys
import inspect
import re
import pickle

import json
import markdown
import pandas as pd
import subprocess
import shutil

from gensim import corpora
from gensim.similarities import Similarity

from GeneradorLSI import GeneradorLSI
from similarity_functions import index2dict
from dict_corp import GenerateDictionary, GenerateCorpus

# Modelo LSI (TF-IDF + SVD)
class TrainLSI(luigi.Task):
	'''Entrena modelos LSI para varios números de tópicos'''

	# Parámetros LSI
	topic_range = luigi.Parameter(default='30,31,1') # Número de topicos. Debe ser una lista de tres números, separados por comas, como las entradas de la función 'range'. Por ejemplo, si se quiere 200 tópicos, '200,201,1'. Si se quiere 10, 15 y 20, '10,21,5', etc
	
	# Parámetros de corpus
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
					'langs':
					{
						idioma:
						{
							n_topics:
							{
								'tfidf':luigi.LocalTarget(os.path.join(self.model_dir,'model-%s-%s-%d.tfidf' % (kind, idioma, n_topics))),
								'lsi-model':luigi.LocalTarget(os.path.join(self.model_dir, 'model-%s-%s-%d.lsi' % (kind, idioma, n_topics))),
								'lsi-index':luigi.LocalTarget(os.path.join(self.model_dir, 'model-%s-%s-%d.lsi.index' % (kind, idioma, n_topics)))
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
class ShowLSI(luigi.Task):
	''''''

	# Parámetros GroupByLSI
	res_dir = luigi.Parameter() # Carpeta para guardar archivos de clasificaciones
	num_similar_docs = luigi.IntParameter(default=5)
	min_similarity = luigi.IntParameter(default=0.5)
	
	# Parámetros TrainLSI
	topic_range = luigi.Parameter(default='30,31,1') #numero de topicos
	
	# Parámetros corpus
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
		return TrainLSI(topic_range=self.topic_range,
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
							n_topics:{
								'json':luigi.LocalTarget(os.path.join(self.res_dir, 'lsi-results-%s-%s-%d.json' % (kind, idioma, n_topics))),
								'csv':luigi.LocalTarget(os.path.join(self.res_dir, 'lsi-results-%s-%s-%d.csv' % (kind, idioma, n_topics))),
								'html':luigi.LocalTarget(os.path.join(self.res_dir, 'lsi-results-table-%s-%s-%d.html' % (kind, idioma, n_topics))),
								'net':luigi.LocalTarget(os.path.join(self.res_dir, 'lsi-results-network-%s-%s-%d.html' % (kind, idioma, n_topics)))
							}
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

				# JSON
				sims = index2dict(index, file_list, num_sims=self.num_similar_docs)
				with o['json'].open('w') as f:
					json.dump(sims, f)

				# HTML + CSV
				s = u''
				net = pd.DataFrame(columns=['from_name', 'to_name', 'sim'])
				for book, v in sims.iteritems():
					s += u'-------------------------------------------\n'
					s += u'### %s\n\n' % (book)
					s += u'| Ranking | Libro | Similitud |\n|:--------:|:-------|-------------:|\n'''
					for rank, attrs in v.iteritems():
						s += u'| %d | %s | %f |\n' % (rank, attrs['name'], round(attrs['similarity'],3))
						net = net.append(pd.DataFrame({'from_name':[book], 'to_name':[attrs['name']], 'sim':[attrs['similarity']]}))
					s += u'\n\n'
				md = markdown.markdown(s, extensions=['markdown.extensions.tables'])
				books = sorted(list(set(net['from_name']).union(net['to_name'])))
				ids = {v:i for i,v in enumerate(books)}
				net['from'] = [ids[k] for k in net['from_name']]
				net['to'] = [ids[k] for k in net['to_name']]

				with o['html'].open('w') as f:
					f.write(md)
				with o['csv'].open('w') as f:
					net.to_csv(f, index=False)

				# Red (en R)
				tempname = 'net_temp0.html'
				i = 1
				while os.path.exists(tempname):
					tempname = 'net_temp%d.html' % i
					i += 1
					if i >= 100:
						print 'ERROR: No se puede crear la red temporal... Checa que no exista un archivo llamado %s en esta carpeta y que tienes permisos de escritura...' % tempname
						break
				subprocess.call(['itam-d3-network', '--input', o['csv'].path, '--output', tempname, '--max_links', str(self.num_similar_docs), '--min_sim', str(self.min_similarity)])
				print 'USER INFO: Creando archivo temporal: ' + tempname
				print 'shutil.move(%s, %s)' % (tempname, o['net'].path)
				shutil.move(tempname, o['net'].path)
				#subprocess.Popen(['mv', tempname, o['net'].path])
				print 'USER INFO: Movimiento listo, %s --> %s' % (tempname, o['net'].path)
				
				if os.path.exists(tempname):
					os.remove(tempname)
				











