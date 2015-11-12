# -*- coding: utf-8 -*-
"""
#DSpaceLoader V2
/scripts/DSpaceLoader.py
#########
#	31/08/2015
#	Sistema desarrollado por el GIL, Instituto de Ingenieria UNAM
#	cgonzalezg@iingen.unam.mx
#	manejador de los scripts localizados en la carpeta de scripts de DSpaceLoader
#########
"""
from datetime import datetime
import logging
import argparse
import sys
import os
import verificadorDependencias
try:
	import extractorXlsx
	import extractorPDFsFileSystem
	import generadorPaquetes
	import cargadorPaquetes
except Exception:
	e = sys.exc_info()
	print e

def verificarParametros(args):
	parser = argparse.ArgumentParser()
	
	parser.add_argument("cantidad_libros", type=int, help="Cantidad de libros a procesar. 0: TODOS LOS LIBROS DISPONIBLES EN EL ARCHIVO DE METADATOS")
	parser.add_argument("ruta_warehouse", help="Carpeta o dirección del warehouse.")
	parser.add_argument("nombre_xlsx", help="Archivo de metadatos.")
	parser.add_argument("carpeta_salida", help="Carpeta en donde se colocarán los libros.")
	parser.add_argument("eperson", help="Eperson de DSpace.")
	
	parametros = parser.parse_args()

	return True, parametros

def extraerXlsx(parametros):
	if os.path.isfile(parametros.nombre_xlsx):
		libros = extractorXlsx.main(("",parametros.nombre_xlsx))
		if libros:
			return True, libros
		else:
			return False, False
	else:
		return False, False

def agruparLibros(parametros):
	parametros_extractorPDFs = list()
	parametros_extractorPDFs.append("")
	parametros_extractorPDFs.append(parametros.cantidad_libros)
	parametros_extractorPDFs.append(parametros.ruta_warehouse)
	parametros_extractorPDFs.append(parametros.carpeta_salida) #carpeta base de salida
	
	bandera, libros_no_agrupados = extractorPDFsFileSystem.main(parametros_extractorPDFs)

	return bandera, libros_no_agrupados

def generarPaquetes(parametros, libros):
	parametros_generadorPaquetes = list()
	parametros_generadorPaquetes.append("")
	parametros_generadorPaquetes.append(parametros.carpeta_salida) #carpeta base de salida
	parametros_generadorPaquetes.append(libros)

	diccionarioColecciones = generadorPaquetes.main(parametros_generadorPaquetes)
	if diccionarioColecciones:
		return True, diccionarioColecciones
	else:
		return False, dict()

def cargarPaquetes(parametros):
	parametros_cargadorPaquetes = list()
	parametros_cargadorPaquetes.append("")
	parametros_cargadorPaquetes.append(parametros.carpeta_salida)
	parametros_cargadorPaquetes.append(parametros.eperson)
	paquetes_no_cargados = cargadorPaquetes.main(parametros_cargadorPaquetes)
	return True, paquetes_no_cargados

def main(args):	
	LOG_FILENAME = 'DSpaceLoader.log'
	logging.basicConfig(filename=LOG_FILENAME, format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

	#sys.stderr = open('DSpaceLoader.err','w')

	#verifica que las dependencias estén instaladas
	bandera = verificadorDependencias.main([""])

	if bandera:
		#verifica que el los parámetros establecidos sean correctos
		bandera, parametros = verificarParametros(args)
		if bandera:
			#extrae la información contenida en el archivo xlsx
			bandera, libros = extraerXlsx(parametros)
			if bandera:
				libros_no_agrupados = list()
				#agrupa las hojas en PDF para hacer los libros
				bandera, libros_no_agrupados = agruparLibros(parametros)
				if bandera:
					#genera los archivo auxiliares necesarios para DSpace
					bandera, diccionarioColecciones = generarPaquetes(parametros, libros)
					if bandera:
						paquetes_no_cargados = list()
						bandera, paquetes_no_cargados = cargarPaquetes(parametros)
						if bandera:
							print "todo LISTO!!"
							print "REPORTE FINAL:"
							print "=============="
							print "libros no agrupados: ", libros_no_agrupados
							print "=============="
							print "paquetes no cargados: ", paquetes_no_cargados
							print "=============="
							print "LOG ESCRITO EN: "+LOG_FILENAME
							
							logging.info("REPORTE FINAL:")
							logging.info("==============")
							logging.info("libros no agrupados:")
							for x in libros_no_agrupados:
								logging.info(x)
							logging.info("==============")
							logging.info("paquetes no cargados:")
							for x in paquetes_no_cargados:
								logging.info(x)
							logging.info("==============")
					else:
						logging.info("Error al crear el contenido de los archivos... Terminando programa.")
						print "Error al crear el contenido de los archivos... Terminando programa."
				else:
					logging.info("Error al unir los PDFs y generar los archivos de texto... Terminando programa.")
					print "Error al unir los PDFs y generar los archivos de texto... Terminando programa."
			else:
				logging.info("Error, el archivo "+parametros.nombre_xlsx+" no existe... Terminando programa.")
				print "Error, el archivo "+parametros.nombre_xlsx+" no existe... Terminando programa."
	else:
		logging.info("Error de dependencias... Terminando programa.")
		print "Error de dependencias... Terminando programa."

if __name__ == '__main__':
    main(sys.argv)


