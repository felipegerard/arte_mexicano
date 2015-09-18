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

#FELIPE# Alterado para mayor flexibilidad de entradas y salidas
class GeneradorLSI(object):
	def __init__(self, ruta_diccionario, ruta_corpus, ruta_modelo_tfidf, ruta_modelo_lsi, ruta_indice, temas):
		self.ruta_diccionario = ruta_diccionario
		self.ruta_corpus = ruta_corpus
		self.ruta_modelo_tfidf = ruta_modelo_tfidf
		self.ruta_modelo_lsi = ruta_modelo_lsi
		self.ruta_indice = ruta_indice
		self.temas = temas
		logging.info("USER INFO: GeneradorLSI creado.")
		print "USER INFO: GeneradorLSI creado."

	def cargarDiccionarioYCorpus(self):
		self.diccionario = corpora.Dictionary.load(self.ruta_diccionario)
		self.corpus = corpora.MmCorpus(self.ruta_corpus)

		return True

	def generarYSerializarTfIdf(self):
		tfidf = models.TfidfModel(self.corpus)
		self.corpus_tfidf = tfidf[self.corpus]
		tfidf.save(self.ruta_modelo_tfidf)
		return True

	def generarYSerializarLSIModel(self):
		LSIModel = models.LsiModel(self.corpus_tfidf, id2word=self.diccionario, num_topics=self.temas)
		LSIModel.print_topics(self.temas)	
		LSIModel.save(self.ruta_modelo_lsi)
		logging.info("Modelo LSI guardado en " + self.ruta_modelo_lsi)
		print "USER INFO: Modelo LSI guardado en " + self.ruta_modelo_lsi

		self.model_LSI = LSIModel
		return True

	def generarYSerializarIndice(self):
		corpus_LSI = self.model_LSI[self.corpus_tfidf]
		indice = similarities.MatrixSimilarity(corpus_LSI) #FELIPE# Posiblemente cambiar a Similarity para que no corra todo en memoria
		indice.save(self.ruta_indice)
		logging.info("Indice de LSI guardado en " + self.ruta_indice)
		print "USER INFO: Indice de LSI guardado en " + self.ruta_indice

		return True

