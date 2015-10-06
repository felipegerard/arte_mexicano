# -*- coding: utf-8 -*-
"""
#TopicModeling V1.1
/scripts/AgrupadorLSI.py
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

class AgrupadorLSI(object):
	def __init__(self, carpeta_salida, listaArchivos, idioma):
		self.carpeta_salida = carpeta_salida
		self.listaArchivos = listaArchivos
		self.idioma = idioma
		self.predicciones = list()
		self.prediccionesDic = dict()
		self.similares = list()
		logging.info("AgrupadorLSI creado.")
		print "AgrupadorLSI creado."

	def cargar(self):
		print "Cargando corpus."
		self.corpus = corpora.MmCorpus(os.path.join(self.carpeta_salida, "corpus_"+self.idioma+".mm"))
		print "Cargando TfIdf."
		self.tfidf = models.TfidfModel.load(os.path.join(self.carpeta_salida,"model_"+self.idioma+".tfidf"))
		print "cargando modelo LSI."
		self.lsi = models.LsiModel.load(os.path.join(self.carpeta_salida,"model_"+self.idioma+".lsi"))
		print "Cargando indice LSI."
		self.indice = similarities.MatrixSimilarity.load(os.path.join(self.carpeta_salida,"model_lsi_"+self.idioma+".index"))

	def agrupar(self):
		for indice, archivo in enumerate(self.listaArchivos):
			sims = self.lsi[self.tfidf[self.corpus[indice]]]
			sims = [[item[0],abs(item[1])] for item in sims]
			self.predicciones.append([sorted(sims, key=lambda item: -item[1])[0], archivo])
		logging.info(str(len(self.listaArchivos))+" textos agrupados.")
		print str(len(self.listaArchivos))+" textos agrupados."
		return True

	#FELIPE# Esto nunca ser usa
	def crearDiccionarioPredicciones(self):
		for grupo,archivo in self.predicciones:
			if grupo not in prediccionesDic:
				self.prediccionesDic[grupo] = list()
			self.prediccionesDic[grupo].append(archivo)
		return self.prediccionesDic

	def calcularDistancias(self):
		similaresDic = dict()
		for indice, archivo in enumerate(self.listaArchivos):
			sims = self.indice[self.lsi[self.tfidf[self.corpus[indice]]]]
			sims = sorted(enumerate(sims), key=lambda item: -item[1])
			self.similares.append((archivo.replace(".txt",""), sims[0:6])) #FELIPE# Se quedan con los primeros 5 hits
		for actual, comparaciones in self.similares:
			tmp = list()
			for idSimilar, angulo in comparaciones:
				tmp.append((self.listaArchivos[idSimilar].replace(".txt",""),angulo))			
			similaresDic[actual] = tmp
		logging.info("Distancias Calculadas!")
		print "Distancias Calculadas!"
		return similaresDic


	def mostrarGrupos(self):
		prediciones_ordenadas = sorted(self.predicciones, key=lambda item:item[0][0])
		for p in prediciones_ordenadas:
			logging.info("grupo: "+str(p[0][0])+ " texto: "+p[1])




