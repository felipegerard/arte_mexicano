# coding=utf-8
#DESPUES DE PREDICTLDA
#ANTES DE TrainLSI
import luigi
import os
import re
import pickle
import json
from pprint import pprint

from lda import TrainLDA, PredictLDA

class ShowLDA(luigi.Task):
	"""Necesita PredictLDA y 
	TrainLDA """
	#variables de ShowLDA
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
	#jpg_dir = luigi.Parameter()
	#image_meta_dir = luigi.Parameter()
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
							#jpg_dir = self.jpg_dir,
							#image_meta_dir = self.image_meta_dir,
							model_dir=self.model_dir,
							meta_dir=self.meta_dir,
							meta_file=self.meta_file,
							lang_file=self.lang_file,
							clean_level=self.clean_level,
							languages=self.languages,
							max_word_length=self.max_word_length,
							min_docs_per_lang=self.min_docs_per_lang),

			'corp_LDA':PredictLDA(res_dir=self.res_dir,
							topic_range=self.topic_range,
							by_chunks=self.by_chunks,
							chunk_size=self.chunk_size,
							update_e=self.update_e,
							n_passes=self.n_passes, 
							pdf_dir=self.pdf_dir,
							txt_dir=self.txt_dir,
							#jpg_dir = self.jpg_dir,
							#image_meta_dir = self.image_meta_dir,
							model_dir=self.model_dir,
							meta_dir=self.meta_dir,
							meta_file=self.meta_file,
							lang_file=self.lang_file,
							clean_level=self.clean_level,
							languages=self.languages,
							max_word_length=self.max_word_length,
							min_docs_per_lang=self.min_docs_per_lang)
						}


################################CHECAR OUTPUT#################
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
							
								 luigi.LocalTarget(os.path.join(self.res_dir, 'lda_results_%s_%s_%d.json' % (kind, idioma, n_topics)))
							
							for n_topics in topic_range
						}
						for idioma in self.input()['corp_LDA']['langs'].iterkeys()
					},
					'files':self.input()['corp_LDA']['files']
				}


	def run(self):
		if self.clean_level in ('raw','clean','stopwords'):
			kind = self.clean_level
		else:
			kind = 'stopwords'

		if not os.path.exists(self.res_dir):
			print 'Creando carpeta para resultados...'
			os.mkdir(self.res_dir)

		for idioma, modelos in self.input()['lda']['langs'].iteritems(): # <<-- n_topics aqui en realidad es un dict con {ntopics:target}. Le cambie el nombre a modelos
			print '======= paso 1 ========='
			# corp_path1 = self.input()['corp_LDA']['langs'][idioma][n_topics]["doc_topics"].path # <<-- Por eso esto no funciona
			# corp_path2 = self.input()['corp_LDA']['langs'][idioma][n_topics]["topics"].path # <<-- Ni esto
			print '------------------------------'
			print 'vamos por buen camino'
			for n_topics, target in modelos.iteritems(): # <<-- No habias definido modelos, pero ahora ya esta y adentro de modelos esta ntopics y target
				print idioma
				# print modelos.keys()
				#corp_path1 = self.input()['corp_LDA']['langs'][idioma][n_topics]["doc_topics"].path
				#corp_path2 = self.input()['corp_LDA']['langs'][idioma][n_topics]["topics"].path
				with self.input()['corp_LDA']['langs'][idioma][n_topics]["doc_topics"].open('r') as f:
					topic_results = pickle.load(f)
				with self.input()['corp_LDA']['langs'][idioma][n_topics]["topics"].open('r') as r:
					topics = pickle.load(r) 
				high_topics = [max(x, key=lambda y: y[1]) for x in topic_results]
				files = [i.replace('.txt', '') for i in os.listdir(os.path.join(self.txt_dir,kind,idioma))]
				res = {
					i:{
						'formula':topic,
						'tags':re.sub(' \+ [\.0-9]+\*', ', ', re.sub('[\.0-9]+\*', '', topic, count=1)),
						'documents':[]
					}
					for i, topic in enumerate(topics)
				}
				for num_doc,(num_topic, s) in enumerate(high_topics):
					res[num_topic]['documents'].append({
							'name':files[num_doc],
							'topic_similarity':s
						})
				pprint(res)

				with self.output()['langs'][idioma][n_topics].open('w') as f:
					json.dump(res, f)
											
