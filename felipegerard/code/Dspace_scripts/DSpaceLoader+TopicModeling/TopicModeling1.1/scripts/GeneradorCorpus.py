# -*- coding: utf-8 -*-
"""
#TopicModeling V1.1
/scripts/GeneradorCorpus.py
#########
#	02/08/2015
#	Sistema desarrollado por el GIL, Instituto de Ingenieria UNAM
#	cgonzalezg@iingen.unam.mx

#########
"""
from gensim import corpora
import os
import io
import logging


class GeneradorCorpus(object):
	def __init__(self, carpeta_textos, carpeta_salida, truncamiento):
		self.carpeta_textos = carpeta_textos
		self.carpeta_salida = carpeta_salida
		self.truncamiento = truncamiento

		logging.info("GeneradorCorpus creado.")
		print "GeneradorCorpus creado."

	def obtenerLibros(self):
		self.archivos = os.listdir(self.carpeta_textos)
		return True

	def cargarArchivo(self, ruta_archivo, corpus, diccionario):
		ap = io.open(ruta_archivo, "r", encoding="utf8")
		contenido = ap.read().replace("\n", " ")
		ap.close()
		if self.truncamiento == 0:
			corpus.append(diccionario.doc2bow(token for token in contenido.lower().split()))
		else:
			corpus.append(diccionario.doc2bow(token[0:self.truncamiento] for token in contenido.lower().split()))


	def generarCorpus(self, idioma):

		diccionario = corpora.Dictionary.load(os.path.join(self.carpeta_salida, "diccionario_"+idioma+".dict"))
		logging.info("Diccionario cargado!")
		print "Diccionario cargado!"
		
		logging.info("Agregar archivos al corpus INICIANDO.")
		print "Agregar archivos al corpus INICIANDO."		
		
		corpus = list()

		for archivo in self.archivos:
			self.cargarArchivo(os.path.join(self.carpeta_textos, archivo), corpus, diccionario)
		
		logging.info("Agregar archivos al corpus FINALIZADO.")
		print "Agregar archivos al corpus FINALIZADO."

		self.corpus = corpus
		return True

	def serializarCorpus(self, idioma):
		direccion_salida = os.path.join(self.carpeta_salida, "corpus_"+idioma+".mm")
		corpora.MmCorpus.serialize(direccion_salida, self.corpus)
		logging.info("Corpus guardado en: "+direccion_salida)
		print "Corpus guardado en: "+direccion_salida
	

