# -*- coding: utf-8 -*-
"""
#TopicModeling V1.1
/scripts/GeneradorDiccionario.py
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
import shutil

class GeneradorDiccionario(object):
	def __init__(self, carpeta_textos, truncamiento):
		self.carpeta_textos = carpeta_textos
		#FELIPE# self.carpeta_salida = carpeta_salida
		self.truncamiento = truncamiento
		self.archivos = os.listdir(self.carpeta_textos)
		logging.info("GeneradorDiccionario creado.")
		print "GeneradorDiccionario creado."

	def obtenerLibros(self):
		return self.archivos


	def generarDiccionario(self):
		#genera diccionario de elementos; asigna un id a cada palabra diferente en el corpus
		diccionario = corpora.Dictionary()
		for archivo in self.archivos:
			self.cargarArchivo(os.path.join(self.carpeta_textos, archivo), diccionario)
		
		#elimina elementos del diccionario con una sola ocurrencia
		#FELIPE# Para pruebas no quito once_ids
		once_ids = [tokenid for tokenid, docfreq in diccionario.dfs.iteritems() if docfreq == 0]
		diccionario.filter_tokens(once_ids)
		#elimina espacios resultantes del eliminado de elementos
		diccionario.compactify()
		self.diccionario = diccionario


	def cargarArchivo(self, ruta_archivo, diccionario):
		ap = io.open(ruta_archivo, "r", encoding="utf8")
		contenido = ap.read().replace("\n", " ")
		ap.close()

		lista_contenido = list()
		if self.truncamiento == 0:
			lista_contenido.append(token for token in contenido.lower().split())
		else:
			lista_contenido.append(token[0:self.truncamiento] for token in contenido.lower().split())
		#agrega los elementos del archivo al diccionario
		diccionario.add_documents(lista_contenido)
		logging.info(ruta_archivo+" agregado al diccionario!")
		print ruta_archivo+" agregado al diccionario!"	

	#FELIPE# Ahora recibe nombre de archivo de salida
	def serializarDiccionario(self, filename):
		direccion_salida = filename #os.path.join(self.carpeta_salida, filename)
		self.diccionario.save(direccion_salida)
		logging.info("diccionario guardado en "+direccion_salida)
		print "diccionario guardado en "+direccion_salida
		

