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
	def __init__(self, carpeta_textos, ruta_diccionario, truncamiento):
		self.carpeta_textos = carpeta_textos
		#FELIPE# self.carpeta_salida = carpeta_salida
		self.ruta_diccionario = ruta_diccionario
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


	def generarCorpus(self):

		# diccionario = corpora.Dictionary.load(os.path.join(self.carpeta_salida, "diccionario_"+idioma+".dict"))
		diccionario = corpora.Dictionary.load(self.ruta_diccionario)
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

	#FELIPE# Ahora recibe nombre de archivo de salida
	def serializarCorpus(self, filename):
		direccion_salida = filename #os.path.join(self.carpeta_salida, "corpus_"+idioma+".mm")
		corpora.MmCorpus.serialize(direccion_salida, self.corpus)
		logging.info("Corpus guardado en: "+direccion_salida)
		print "Corpus guardado en: "+direccion_salida
	

