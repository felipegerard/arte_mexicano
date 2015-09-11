# -*- coding: utf-8 -*-
"""
#TopicModeling V1.1
/scripts/pdf2txt.py
#########
#	02/08/2015
#	Sistema desarrollado por el GIL, Instituto de Ingenieria UNAM
#	cgonzalezg@iingen.unam.mx

# Modificaciones:
# Autor				Fecha			Cambios
# Felipe Gerard		2015-09-10		Ejecución en pipeline
#########
"""

### Agregado try catch por si no está instalado cStringIO
try:
	from cStringIO import StringIO
except:
	from StringIO import StringIO
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
	##### Hardcodeado feo
	#return [os.path.join(rutaGeneral,x,x.split("_DSPACE")[0]) for x in os.listdir(rutaGeneral) if "_DSPACE" in x]
	return [os.path.join(rutaGeneral,x) for x in os.listdir(rutaGeneral)]

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

#FELIPE#
def guardarContenido(rutaBaseTXTs,idioma,nombreLibro,contenido):
        # nombreLibro = os.path.join(rutaBaseTXTs,idioma,nombreLibro+".txt")
        nombreLibro = os.path.join(rutaBaseTXTs,'books',nombreLibro+".txt")

        # if not os.path.exists(os.path.join(rutaBaseTXTs,idioma)):
        #         logging.info("Creando carpeta de idioma: "+os.path.join(rutaBaseTXTs,idioma))
        #         print "Creando carpeta de idioma: "+os.path.join(rutaBaseTXTs,idioma)
        #         os.makedirs(os.path.join(rutaBaseTXTs,idioma))

        ap = open(nombreLibro,"w")
        ap.write(contenido)
        ap.close()
        print nombreLibro + " guardado en " + nombreLibro

#FELIPE#
def extraerVolumenes(inputPDF,rutaBaseTXTs,librosNoConvertidos):
	agregados = []
	for pdf in inputPDF:
		print "---------------------------------"
		print "Convirtiendo "+pdf.path
		rutaVolumenes = obtenerRutaVolumenes(pdf.path)
		contenido = convertirVolumenes(rutaVolumenes)
		idioma = detectarIdioma(contenido)	
		nombreLibro = os.path.split(pdf.path)[-1]
		print idioma+": "+nombreLibro
		guardarContenido(rutaBaseTXTs,idioma,nombreLibro,contenido)
		
		agregados.append(idioma + '\t' + nombreLibro)
	with open(os.path.join(rutaBaseTXTs,"librosAgregados.tm"),'w') as ap:
			ap.writelines('\n'.join(agregados))



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

# def main(args):	

# 	rutaGeneral = args[1] #libros/
# 	rutaBaseTXTs = args[2]
# 	librosNoConvertidos = list()
	
# 	if not os.path.exists(rutaBaseTXTs):
# 		logging.info("Creando carpeta base para archivos txt.")
# 		print "Creando carpeta base para archivos txt."
# 		os.makedirs(rutaBaseTXTs)
	
# 	rutasBasePDF = obtenerRutasBasePDF(rutaGeneral)
# 	#####
# 	print rutasBasePDF
# 	for i,d in enumerate(rutasBasePDF):
# 		print i, ': ', d
# 	extraerVolumenes(rutasBasePDF,rutaBaseTXTs,librosNoConvertidos)

# 	return True, librosNoConvertidos

# if __name__ == '__main__':
#     main(sys.argv)


