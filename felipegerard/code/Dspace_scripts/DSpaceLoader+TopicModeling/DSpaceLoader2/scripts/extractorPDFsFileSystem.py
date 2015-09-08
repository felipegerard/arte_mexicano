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

def natural_key(string_):
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_[0])]

def convert(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = file(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text

def obtener_carpetas_base(carpeta_base,cantidad_libros):
	#cantidad_libros = 500
	if cantidad_libros == 0:
		return os.listdir(carpeta_base)
	else:
		return os.listdir(carpeta_base)[:cantidad_libros]

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

def generar_libros(warehouse,carpetas_base_libros, carpeta_salida_libros, libros_no_agrupados):
	i = 1
	bandera = False
	for carpeta_base_libro in carpetas_base_libros:
		if os.path.exists(os.path.join(carpeta_salida_libros,carpeta_base_libro+"_DSPACE")):
			logging.info("El libro "+carpeta_base_libro+" ya ha sido procesado; saltando..")
			print "El libro "+carpeta_base_libro+" ya ha sido procesado; saltando.."
			libros_no_agrupados.append(os.path.join(carpeta_salida_libros,carpeta_base_libro))
		else:		
			if os.path.exists(os.path.join(carpeta_salida_libros,carpeta_base_libro)):
				logging.info("Eliminando carpeta antigua: "+carpeta_base_libro)
				print "Eliminando carpeta antigua: "+carpeta_base_libro
				shutil.rmtree(os.path.join(carpeta_salida_libros,carpeta_base_libro))
			os.makedirs(os.path.join(carpeta_salida_libros,carpeta_base_libro))
			logging.info("Agrupando: "+carpeta_base_libro)
			print "Agrupando: "+carpeta_base_libro
			lista_hojas_pdf, portada_jpg = obtener_contenido_libro(os.path.join(warehouse, carpeta_base_libro))
			
			if len(lista_hojas_pdf) > 0 and portada_jpg:
				bandera = generar_libro(carpeta_base_libro,lista_hojas_pdf,portada_jpg,carpeta_salida_libros)
			else:
				logging.info("NO ES POSIBLE AGRUPAR "+carpeta_base_libro)
				print "NO ES POSIBLE AGRUPAR "+carpeta_base_libro
				libros_no_agrupados.append(os.path.join(carpeta_salida_libros,carpeta_base_libro))
				bandera = False
			if bandera == False:
				logging.info("BORRANDO CARPETA DEL LIBRO "+carpeta_base_libro+" DEBIDO A ERRORES...")
				print "BORRANDO CARPETA DEL LIBRO "+carpeta_base_libro+" DEBIDO A ERRORES..."
				shutil.rmtree(os.path.join(carpeta_salida_libros,carpeta_base_libro))
		logging.info("procesado "+str(i)+"/"+str(len(carpetas_base_libros)))
		print "procesado "+str(i)+"/"+str(len(carpetas_base_libros))
		i = i+1
	logging.info("Se han creado todos los libros")
	print "Se han creado todos los libros"


def obtener_peso_libro(lista_hojas_pdf):
	return reduce(lambda (a,x),(b,y): (0,x+y), lista_hojas_pdf)[1]


def generar_libro(carpeta_base_libro,lista_hojas_pdf,portada_jpg,carpeta_salida_libros):
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
	try:
		shutil.copy(portada_jpg,os.path.join(carpeta_merge,nombre+".jpg"))
	except:
		logging.info("No se pudo copiar la imagen de portada.")
		print "No se pudo copiar la imagen de portada."
		return False
	return True

def main(args):	
	if args[0] != "":
		print "NO ES POSIBLE EJECUTAR EL SCRIPT. FAVOR DE UTILIZAR DSpaceLoader.sh"
		return False

	cantidad_libros = args[1]
	warehouse = args[2]
	carpeta_salida_libros = args[3]
	libros_no_agrupados = list()

	carpetas_base_libros = obtener_carpetas_base(warehouse,cantidad_libros)
	generar_libros(warehouse,carpetas_base_libros, carpeta_salida_libros, libros_no_agrupados)

	return True, libros_no_agrupados
if __name__ == '__main__':
    main(sys.argv)


