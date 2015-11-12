# -*- coding: utf-8 -*-
import luigi
import os
import sys
import inspect
import re
import shutil
import json
import logging
from xml_similarity_fucntions import *

def generarSeccion(libro, listaSimilares):
	#self.url = http://200.66.82.41:8080
	url_base='http://200.66.82.41:8080'
	cadena = "\n\t<libro handle=\"123456789/"+libro+"\">"
	for nombre,url in listaSimilares:
		nombre = nombre.replace("_"," ")
		nombre = nombre.replace("&","&amp;")
		nombre = nombre.replace("\"","&quot;")
		nombre = nombre.replace("<", "&lt;")
		nombre = nombre.replace(">", "&gt;")
		nombre = nombre.replace("'", "&apos;")
		nombre = nombre.title()
		cadena += "\n\t\t<similar>"
		cadena += "\n\t\t\t<titulo>"+nombre+"</titulo>"
		cadena += "\n\t\t\t<href>"+url_base+"/xmlui/handle/123456789/"+url+"</href>"
		cadena += "\n\t\t</similar>"
	cadena += "\n\t</libro>"
	return cadena

def extraerSimilares(lista_libros):
	contenido = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n\n<similitud>"
	#print self.similares
	for libro in lista_libros:
		listaSimilares = list()
		similares = lista_libros[libro]
		for nombre,similitud in similares:
			# if nombre != libro and similitud >= 0.5:
			if nombre != libro:
				listaSimilares.append(nombre)
		contenido += generarSeccion(libro,listaSimilares)
	contenido += "</similitud>"
	return contenido