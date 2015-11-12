# -*- coding: utf-8 -*-
"""
#DSpaceLoader V2
/scripts/extractorPDFsFileSystem.py
#########
#	31/08/2015
#	Sistema desarrollado por el GIL, Instituto de Ingenieria UNAM
#	cgonzalezg@iingen.unam.mx

#	return: 
#		True -> si todo sale bien
#		False -> si hay algún error
#
#		libros_no_agrupados
#########
"""

from PyPDF2 import PdfFileReader,PdfFileMerger
from cStringIO import StringIO
from math import ceil
import os
import logging
import io
import shutil
import sys
import re

def obtener_contenido_libro(ruta_libro):
	lista_hojas_pdf = list()
	lista_hojas_jpg = list()
	portada_jpg = False

	try:
		lista_hojas_pdf = [[os.path.join(ruta_libro,"pdf",x),float(os.path.getsize(os.path.join(ruta_libro,"pdf",x)))] for x in os.listdir(os.path.join(ruta_libro,"pdf")) if ".pdf" in x]		
		portada_pdf = [x for x in lista_hojas_pdf if "por_" in x[0]][0]
		lista_hojas_pdf.remove(portada_pdf)
		lista_hojas_pdf = sorted(lista_hojas_pdf,key=natural_key)
		lista_hojas_pdf.insert(0,portada_pdf)
		lista_hojas_jpg = [os.path.join(ruta_libro,"jpg",x) for x in os.listdir(os.path.join(ruta_libro,"jpg"))]		
	except:
		logging.info("No existe la carpeta 'pdf' y/o no existe la carpeta 'jpg' dentro de "+ruta_libro)
		print "No existe la carpeta 'pdf' y/o no existe la carpeta 'jpg' dentro de "+ruta_libro
		e = sys.exc_info()
		print e

		return [], False
	
	try:
		portada_jpg = [x for x in lista_hojas_jpg if "por_" in x][0]
	except:
		logging.info("No existe la hoja de portada en /jpg")
		print "No existe la hoja de portada en /jpg"

	if portada_jpg and len(lista_hojas_pdf) > 0:
		return lista_hojas_pdf, portada_jpg
	else:
		return [], False

def obtener_peso_libro(lista_hojas_pdf):
	return reduce(lambda (a,x),(b,y): (0,x+y), lista_hojas_pdf)[1]

def generar_libro(carpeta_base_libro,lista_hojas_pdf,carpeta_salida_libros):
	salida_PDF = PdfFileMerger()
	limite = 52428800.0
	tam_actual = 0.0
	indice = 1
	ciclo = 1

	carpeta_merge = os.path.join(carpeta_salida_libros,carpeta_base_libro.split("/")[-1])
	nombre = carpeta_base_libro.split("/")[-1]
	divisiones = int(ceil(obtener_peso_libro(lista_hojas_pdf)/limite))

	for hoja_pdf,peso_pdf in lista_hojas_pdf:
		try:
			entrada_PDF = PdfFileReader(io.open(hoja_pdf, "rb"))
		except:
			logging.info("Error al agregar "+hoja_pdf)
			print "Error al agregar "+hoja_pdf
		else:
			salida_PDF.append(entrada_PDF)				
			tam_actual += peso_pdf			
			if tam_actual > limite or ciclo == len(lista_hojas_pdf):
				archivo_salida_PDF = open(os.path.join(carpeta_merge,nombre+"_"+str(indice)+"de"+str(divisiones)+".pdf"), "wb")	
				try:
					salida_PDF.write(archivo_salida_PDF)	
					archivo_salida_PDF.close()
					logging.info("Se ha creado el volumen "+os.path.join(carpeta_merge,nombre+"_"+str(indice)+"de"+str(divisiones)+".pdf"))
					print "Se ha creado el volumen "+os.path.join(carpeta_merge,nombre+"_"+str(indice)+"de"+str(divisiones)+".pdf")
					salida_PDF = PdfFileMerger()
					indice += 1	
					tam_actual = 0.0
				except:
					logging.info("NO SE PUDO CREAR EL VOLUMEN "+os.path.join(carpeta_merge,nombre+"_"+str(indice)+"de"+str(divisiones)+".pdf"))
					print "NO SE PUDO CREAR EL VOLUMEN "+os.path.join(carpeta_merge,nombre+"_"+str(indice)+"de"+str(divisiones)+".pdf")
		ciclo += 1
	return True