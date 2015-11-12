# -*- coding: utf-8 -*-
"""
#TopicModeling V2
/scripts/TopicModeling.py
#########
#	02/08/2015
#	Sistema desarrollado por el GIL, Instituto de Ingenieria UNAM
#	cgonzalezg@iingen.unam.mx
#	manejador de los scripts localizados en la carpeta de scripts de TopicModeling
#########
"""
import sys
import os
import logging
import shutil
LOG_FILENAME = 'TopicModeling.log'
logging.basicConfig(filename=LOG_FILENAME, format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import argparse
import verificadorPaquetes
try:
	import pdf2txt
	from GeneradorDiccionario import GeneradorDiccionario
	from GeneradorCorpus import GeneradorCorpus
	from GeneradorLSI import GeneradorLSI
	from AgrupadorLSI import AgrupadorLSI
	from GeneradorXML import GeneradorXML
except Exception:
	e = sys.exc_info()
	print e

def verificarParametros(args):
	print args
        parser = argparse.ArgumentParser()

        parser.add_argument("ruta_general", help="Carpeta en donde se localizan los libros.")
        parser.add_argument("ruta_base_txts", help="Carpeta en donde se colocarán los libros en txt.")
        parser.add_argument("ruta_lsi", help="Carpeta en donde se almacenarán las estructuras de LSI.")
        parser.add_argument("ruta_xml", help="Carpeta en donde se colocará el archivo xml.")
        parser.add_argument("bd_usuario", help="Usuario de la base de datos.")
	parser.add_argument("bd_password", help="Contraseña del usuario de la base de datos.")
	parser.add_argument("url_base", help="Dirección y puerto de la instalación de DSpace.")
        parametros = parser.parse_args()

        return True, parametros

def convertirLibros(parametros):
	parametros_pdf2txt = list()
	parametros_pdf2txt.append("")
	parametros_pdf2txt.append(parametros.ruta_general)
	parametros_pdf2txt.append(parametros.ruta_base_txts)
	bandera, librosNoConvertidos = pdf2txt.main(parametros_pdf2txt)
	return bandera, librosNoConvertidos


def obtenerCarpetasDeIdioma(rutaBaseTXTs):
	return os.listdir(rutaBaseTXTs)

def generarDiccionario(carpeta_textos, carpeta_salida, truncamiento, idioma):
	generadorDiccionario = GeneradorDiccionario(carpeta_textos, carpeta_salida, truncamiento)
	listaArchivos = generadorDiccionario.obtenerLibros()
	generadorDiccionario.generarDiccionario()
	generadorDiccionario.serializarDiccionario(idioma)
	return listaArchivos

def generarCorpus(carpeta_textos, carpeta_salida, truncamiento, idioma):
	generadorCorpus = GeneradorCorpus(carpeta_textos, carpeta_salida, truncamiento)
	generadorCorpus.obtenerLibros()
	generadorCorpus.generarCorpus(idioma)
	generadorCorpus.serializarCorpus(idioma)


def generarLSI(carpeta_salida, cantidad_temas, idioma):
	generadorLSI = GeneradorLSI(carpeta_salida, cantidad_temas)
	generadorLSI.cargarDiccionarioYCorpus(idioma)
	generadorLSI.generarYSerializarTfIdf(idioma)
	generadorLSI.generarYSerializarLSIModel(idioma)
	generadorLSI.generarYSerializarIndice(idioma)

def agruparLSI(carpeta_salida, listaArchivos, idioma):
	agrupadorLSI = AgrupadorLSI(carpeta_salida, listaArchivos, idioma)
	agrupadorLSI.cargarCorpus()
	agrupadorLSI.cargarTfIdf()
	agrupadorLSI.cargarLSIModel()
	agrupadorLSI.cargarIndiceLSI()
	agrupadorLSI.agrupar()
	agrupadorLSI.mostrarGrupos()
	similares = agrupadorLSI.calcularDistancias()
	return similares
	


def iniciarModelado(parametros):
	similaresTodos = dict()
	idiomas = obtenerCarpetasDeIdioma(parametros.ruta_base_txts)
	try:
		idiomas.remove('librosAgregados.tm')
		idiomas.remove('swedish') 
	except Exception:
		print ""	
	if os.path.exists(parametros.ruta_lsi):
		shutil.rmtree(parametros.ruta_lsi)
		logging.info("Borrando carpeta LSI.")
		print "Borrando carpeta LSI."
	os.makedirs(parametros.ruta_lsi)
	logging.info("Creando carpeta LSI.")
	print "Creando carpeta LSI."
	for idioma in idiomas:
		logging.info("Procesando idioma "+idioma)
		print "Procesando idioma "+idioma
		rutaTextos = os.path.join(parametros.ruta_base_txts,idioma)
		if len(os.listdir(rutaTextos)) < 2:
			logging.info("No hay suficientes muestras para generar el modelo. Omitiendo idioma.")
			print "No hay suficientes muestras para generar el modelo. Omitiendo idioma."
			continue
		listaArchivos = generarDiccionario(rutaTextos, parametros.ruta_lsi, 6, idioma)
		generarCorpus(rutaTextos, parametros.ruta_lsi, 6, idioma)
		generarLSI(parametros.ruta_lsi, 200, idioma)
		similares = agruparLSI(parametros.ruta_lsi,listaArchivos,idioma)
		for similar in similares:
			similaresTodos[similar] = similares[similar]
	return similaresTodos

def generarXML(parametros, similaresTodos):
	generadorXML = GeneradorXML(parametros.ruta_xml,similaresTodos,parametros.bd_usuario,parametros.bd_password,parametros.url_base)
	generadorXML.extraerSimilares()
	generadorXML.escribirXML()
	return True

def main(args):
	logging.info("====INICIANDO TOPICMODELING===")
	parametros = dict()

	bandera = verificadorPaquetes.main([""])

	if bandera:
		bandera, parametros = verificarParametros(args)
		if bandera:
			bandera, librosNoConvertidos = convertirLibros(parametros)
			if bandera:
				similaresTodos = iniciarModelado(parametros)
				generarXML(parametros, similaresTodos)
				print "TODO LISTO! Saliendo..."
				logging.info("TODO LISTO! Saliendo...")
			else:
				logging.info("Error al convertir los libros.")
				print "Error al convertir los libros"
	else:
		logging.info("Error de dependencias... Terminando programa.")
		print "Error de dependencias... Terminando programa."

if __name__ == '__main__':
    main(sys.argv)
