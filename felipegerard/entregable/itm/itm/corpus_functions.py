# coding=utf-8

from gensim import corpora
import os
import io
import logging

def cargarArchivo(ruta_archivo, corpus, diccionario, truncamiento=6):
	ap = io.open(ruta_archivo, "r", encoding="utf8")
	contenido = ap.read().replace("\n", " ")
	ap.close()
	if truncamiento == 0:
		corpus.append(diccionario.doc2bow(token for token in contenido.lower().split()))
	else:
		corpus.append(diccionario.doc2bow(token[0:truncamiento] for token in contenido.lower().split()))

def generarCorpus(ruta_diccionario, carpeta_textos, truncamiento=6):
	diccionario = corpora.Dictionary.load(ruta_diccionario)
	logging.info("Diccionario cargado!")
	print "USER INFO: Diccionario cargado!"
	
	logging.info("Agregar archivos al corpus INICIANDO.")
	print "USER INFO: Agregar archivos al corpus INICIANDO."
	archivos = os.listdir(carpeta_textos)
	corpus = list()
	for archivo in archivos:
		cargarArchivo(os.path.join(carpeta_textos, archivo), corpus, diccionario, truncamiento)
	
	logging.info("Agregar archivos al corpus FINALIZADO.")
	print "USER INFO: Agregar archivos al corpus FINALIZADO."
	return corpus














