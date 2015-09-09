# -*- coding: utf-8 -*-
"""
#TopicModeling V1.1
/scripts/pdf2txt.py
#########
#	02/08/2015
#	Sistema desarrollado por el GIL, Instituto de Ingenieria UNAM
#	cgonzalezg@iingen.unam.mx

#########
"""

from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from nltk import wordpunct_tokenize
from nltk.corpus import stopwords
import os
import io
import sys
import logging
import shutil

def convertir(rutaVolumen, hojas=None):
    if not hojas:
        hojas = set()
    else:
        hojas = set(hojas)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = file(rutaVolumen, 'rb')
    for hoja in PDFPage.get_pages(infile, hojas):
        interpreter.process_page(hoja)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text

def obtenerRutasBasePDF(rutaGeneral):
	return [os.path.join(rutaGeneral,x,x.split("_DSPACE")[0]) for x in os.listdir(rutaGeneral) if "_DSPACE" in x]

def obtenerRutaVolumenes(rutaBasePDF):
	return [os.path.join(rutaBasePDF,x) for x in os.listdir(rutaBasePDF) if ".pdf" in x]

def convertirVolumenes(rutaVolumenes):
	txt = ""
	for rutaVolumen in rutaVolumenes:
		try:
			txt += convertir(rutaVolumen)
		except Exception:
			logging.info("ERROR al convertir el volumen "+rutaVolumen)
			print "ERROR al convertir el volumen "+rutaVolumen

	return txt

def agregarARegistro(rutaBaseTXTs,rutaBasePDF):
	bandera = True
	ap = open(os.path.join(rutaBaseTXTs,"librosAgregados.tm"),"a+")
	contenido = ap.readlines()
	if rutaBasePDF+"\n" in contenido:
		bandera = False
	else:
		ap.write(rutaBasePDF+"\n")
	ap.close()
	return bandera


def guardarContenido(rutaBaseTXTs,idioma,nombreLibro,contenido):
	nombreLibro = os.path.join(rutaBaseTXTs,idioma,nombreLibro+".txt")

	if not os.path.exists(os.path.join(rutaBaseTXTs,idioma)):
		logging.info("Creando carpeta de idioma: "+os.path.join(rutaBaseTXTs,idioma))
		print "Creando carpeta de idioma: "+os.path.join(rutaBaseTXTs,idioma)
		os.makedirs(os.path.join(rutaBaseTXTs,idioma))

	ap = open(nombreLibro,"w")
	ap.write(contenido)
	ap.close()
	logging.info(nombreLibro+" guardado en " + nombreLibro)
	print nombreLibro + " guardado en " + nombreLibro


def extraerVolumenes(rutasBasePDF,rutaBaseTXTs,librosNoConvertidos):
	for rutaBasePDF in rutasBasePDF:
		logging.info("Convirtiendo "+rutaBasePDF)
		print "Convirtiendo "+rutaBasePDF
		if agregarARegistro(rutaBaseTXTs,rutaBasePDF):
			rutaVolumenes = obtenerRutaVolumenes(rutaBasePDF)
			contenido = convertirVolumenes(rutaVolumenes)
			idioma = detectarIdioma(contenido)	
			nombreLibro = os.path.split(rutaBasePDF)[-1]
		
			logging.info(idioma+": "+nombreLibro)
			print idioma+": "+nombreLibro
			guardarContenido(rutaBaseTXTs,idioma,nombreLibro,contenido)
		else:
			logging.info("El libro ya ha sido convertido.")
			print "El libro ya ha sido convertido."
def calcularValoresDeIdioma(contenido):

	languages_ratios = {}

	tokens = wordpunct_tokenize(contenido)
	words = [word.lower() for word in tokens]

	for language in stopwords.fileids():
		stopwords_set = set(stopwords.words(language))
		words_set = set(words)
		common_elements = words_set.intersection(stopwords_set)

		languages_ratios[language] = len(common_elements)

	return languages_ratios

def detectarIdioma(contenido):

	valores = calcularValoresDeIdioma(contenido)

	idioma = max(valores, key=valores.get)

	return idioma

def main(args):	

	rutaGeneral = args[1] #libros/
	rutaBaseTXTs = args[2]
	librosNoConvertidos = list()
	
	if not os.path.exists(rutaBaseTXTs):
		logging.info("Creando carpeta base para archivos txt.")
		print "Creando carpeta base para archivos txt."
		os.makedirs(rutaBaseTXTs)
	
	rutasBasePDF = obtenerRutasBasePDF(rutaGeneral)
	extraerVolumenes(rutasBasePDF,rutaBaseTXTs,librosNoConvertidos)

	return True, librosNoConvertidos

if __name__ == '__main__':
    main(sys.argv)


