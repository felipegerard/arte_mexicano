# coding=utf-8

from gensim import corpora
import os
import io
import logging
import shutil

nombre_diccionario = self.output()['langs'][idioma].path
generadorDiccionario = GeneradorDiccionario(rutaTextos, truncamiento=self.max_word_length)
generadorDiccionario.generarDiccionario()
generadorDiccionario.serializarDiccionario(nombre_diccionario)


def cargarArchivo(ruta_archivo, diccionario, truncamiento=6):
	ap = io.open(ruta_archivo, "r", encoding="utf8")
	contenido = ap.read().replace("\n", " ")
	ap.close()

	lista_contenido = list()
	if truncamiento == 0:
		lista_contenido.append(token for token in contenido.lower().split())
	else:
		lista_contenido.append(token[0:truncamiento] for token in contenido.lower().split())
	#agrega los elementos del archivo al diccionario
	diccionario.add_documents(lista_contenido)
	logging.info(ruta_archivo+" agregado al diccionario!")
	print 'USER INFO: ' + ruta_archivo + " agregado al diccionario!"

def generarDiccionario(carpeta_textos, min_doc_freq=0, truncamiento=6):
	#genera diccionario de elementos; asigna un id a cada palabra diferente en el corpus
	diccionario = corpora.Dictionary()
	for archivo in self.archivos:
		cargarArchivo(os.path.join(carpeta_textos, archivo), diccionario, truncamiento)
	
	#elimina elementos del diccionario con una sola ocurrencia
	#FELIPE# Para pruebas no quito once_ids
	once_ids = [tokenid for tokenid, docfreq in diccionario.dfs.iteritems() if docfreq <= min_doc_freq]
	diccionario.filter_tokens(once_ids)
	#elimina espacios resultantes del eliminado de elementos
	diccionario.compactify()
	return diccionario

def serializarDiccionario(diccionario, filename):
	diccionario.save(filename)
	logging.info("diccionario guardado en " + direccion_salida)
	print "USER INFO: Diccionario guardado en " + direccion_salida













