# -*- coding: utf-8 -*-
"""
#TopicModeling V1.1
/scripts/GeneradorLSI.py
#########
#	02/08/2015
#	Sistema desarrollado por el GIL, Instituto de Ingenieria UNAM
#	cgonzalezg@iingen.unam.mx

#########
"""
from gensim import corpora, models, similarities
import os
import io
import logging

class GeneradorLSI(object):
	def __init__(self, carpeta_salida, temas):
		self.carpeta_salida = carpeta_salida
		self.temas = temas
		logging.info("GeneradorLSI creado.")
		print "GeneradorLSI creado."

	def cargarDiccionarioYCorpus(self, idioma):
		self.diccionario = corpora.Dictionary.load(os.path.join(self.carpeta_salida, "diccionario_"+idioma+".dict"))
		self.corpus = corpora.MmCorpus(os.path.join(self.carpeta_salida, "corpus_"+idioma+".mm"))

		return True

	def generarYSerializarTfIdf(self, idioma):
		tfidf = models.TfidfModel(self.corpus)
		self.corpus_tfidf = tfidf[self.corpus]
		tfidf.save(os.path.join(self.carpeta_salida,"model_"+idioma+".tfidf"))
		return True

	def generarYSerializarLSIModel(self, idioma):
		LSIModel = models.LsiModel(self.corpus_tfidf, id2word=self.diccionario, num_topics=self.temas)
		LSIModel.print_topics(self.temas)	
		LSIModel.save(os.path.join(self.carpeta_salida,"model_"+idioma+".lsi"))
		logging.info("Modelo LSI guardado en "+os.path.join(self.carpeta_salida,"model_"+idioma+".lsi"))
		print "Modelo LSI guardado en "+os.path.join(self.carpeta_salida,"model_"+idioma+".lsi")

		self.model_LSI = LSIModel
		return True

	def generarYSerializarIndice(self, idioma):
		corpus_LSI = self.model_LSI[self.corpus_tfidf]
		indice = similarities.MatrixSimilarity(corpus_LSI)
		indice.save(os.path.join(self.carpeta_salida,"model_lsi_"+idioma+".index"))
		logging.info("Indice de LSI guardado en "+os.path.join(self.carpeta_salida,"model_lsi_"+idioma+".index"))
		print "Indice de LSI guardado en "+os.path.join(self.carpeta_salida,"model_lsi_"+idioma+".index")

		return True

