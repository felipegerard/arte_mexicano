# -*- coding: utf-8 -*-
"""
#DSpaceLoader V2
/scripts/generadorPaquetes.py
#########
#	31/08/2015
#	Sistema desarrollado por el GIL, Instituto de Ingenieria UNAM
#	cgonzalezg@iingen.unam.mx
#	Crea los archivos necesarios para DSpace
#	return: un diccionario con información referente a la colección a la
#	que pertenece cada libro
#########
"""
import shutil
import sys
import os
import logging
import io

def generarContenidoXML(parametros):
	titulo = "NA" if ("N/A" or "NA") in parametros["titulo"].upper() else  parametros["titulo"].replace("&","&#x26;").replace("_","&#x20;").capitalize()
	autor = "NA" if ("N/A" or "NA") in parametros["autor"].upper() else parametros["autor"].replace("&","&#x26;").replace(" ","&#x20;")
	contenido ="""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<dublin_core schema="dc">
  <dcvalue element="contributor" qualifier="author">"""+autor+"""</dcvalue>
  <dcvalue element="date" qualifier="issued">"""+parametros["ano"].replace("_","&#x20;")+"""</dcvalue>
  <dcvalue element="title" qualifier="none" language="en_US">"""+titulo+"""</dcvalue>
  <dcvalue element="type" qualifier="none" language="en_US">Book</dcvalue>
</dublin_core>"""

	return contenido


def generarContenidoContents(parametros,volumenes):
	contenido = ""
	for volumen in volumenes:
		contenido +=volumen+"	bundle:ORIGINAL	description:libro\n"
	contenido += "license.txt	bundle:LICENSE\n" 
	contenido += parametros["titulo"]+".jpg	bundle:ORIGINAL	description:Imagen de portada"

	return contenido

def obtenerCarpetasLibro(carpetaBase):
	return os.listdir(carpetaBase)

def obtenerVolumenes(carpetaLibro):
	return [x for x in os.listdir(carpetaLibro) if ".pdf" in x]

def generarDiccionarioDeLibros(listaLibros):

	diccionarioLibros = dict()
	for libro in listaLibros:
		tmp = dict()
		#cambio temporal
		tmp["Titulo"] = libro["Final"].replace(" ","_")
		if type(libro["Autor"]) == int:
			tmp["Autor"] = str(libro["Autor"])
		else:
			tmp["Autor"] = libro["Autor"]
		tmp["Coleccion"] = libro["Colección".decode("utf8")]
		tmp["Licencia"] = libro["Licencia"]
		if type(libro["Año de Edición".decode("utf8")]) == int:
			if libro["Año de Edición".decode("utf8")] == 0:
				tmp["AnoEdicion"] = "0000"
			else:
				tmp["AnoEdicion"] = str(libro["Año de Edición".decode("utf8")])
		else:
			tmp["AnoEdicion"] = "1001"
		#cambio temporal por la inconsistencia del formato
		diccionarioLibros[libro["Final"].replace(" ","_")] = tmp

	return diccionarioLibros

def crearPaquete(carpetaBase, datosLibro,volumenes):


	parametros = dict()
	parametros["autor"] = datosLibro["Autor"]
	parametros["ano"] = datosLibro["AnoEdicion"]
	parametros["titulo"] = datosLibro["Titulo"]
	parametros["coleccion"] = str(datosLibro["Coleccion"])
	parametros["licencia"] = datosLibro["Licencia"]
	contenidoXML = generarContenidoXML(parametros)

	contenidoContents = generarContenidoContents(parametros,volumenes)

	
	archivoXML = io.open(os.path.join(carpetaBase,parametros["titulo"],"dublin_core.xml"), "w")
	archivoXML.write(contenidoXML)
	archivoXML.close()	

	archivoLicencia = io.open(os.path.join(carpetaBase,parametros["titulo"],"license.txt"), "w")
	archivoLicencia.write(parametros["licencia"])
	archivoLicencia.close()	

	archivoContents = io.open(os.path.join(carpetaBase,parametros["titulo"],"contents"), "w")
	archivoContents.write(contenidoContents)
	archivoContents.close()	

	archivoCollection = io.open(os.path.join(carpetaBase,parametros["titulo"],"coleccion"), "w")
	archivoCollection.write(unicode(parametros["coleccion"]))
	archivoCollection.close	

	logging.info("Paquete "+os.path.join(carpetaBase,parametros["titulo"])+" creado")
	print "Paquete "+os.path.join(carpetaBase,parametros["titulo"])+" creado"

	return parametros["coleccion"], parametros["titulo"]
	
def finalizarPaquete(carpetaBase, libroExistente):
	logging.info("Finalizando paquete "+libroExistente)
	print "Finalizando paquete "+libroExistente
	archivos = os.listdir(os.path.join(carpetaBase,libroExistente))
	archivos.remove("coleccion")
	os.makedirs(os.path.join(carpetaBase,libroExistente,libroExistente))
	for archivo in archivos:
		shutil.move(os.path.join(carpetaBase,libroExistente,archivo),os.path.join(carpetaBase,libroExistente,libroExistente,archivo))
	os.rename(os.path.join(carpetaBase,libroExistente),os.path.join(carpetaBase,libroExistente+"_DSPACE"))
	logging.info("Paquete finalizado")
	print "Paquete finalizado"

def main(args):	
	if args[0] != "":
		print "NO ES POSIBLE EJECUTAR EL SCRIPT. FAVOR DE UTILIZAR DSpaceLoader.sh"
		return False

	carpetaBase = args[1]
	listaLibros = args[2]

	librosExistentes = obtenerCarpetasLibro(carpetaBase)
	diccionarioLibros = generarDiccionarioDeLibros(listaLibros)
	
	diccionarioColecciones = dict() # {"4":[carpeta_1,carpeta3],"5":[carpeta_2,carpeta_5]}

	for libroExistente in librosExistentes:
		if libroExistente in diccionarioLibros:
			volumenes = obtenerVolumenes(os.path.join(carpetaBase,libroExistente))
			coleccion, carpeta = crearPaquete(carpetaBase, diccionarioLibros[libroExistente],volumenes)
			finalizarPaquete(carpetaBase,libroExistente)
			if coleccion in diccionarioColecciones:
				diccionarioColecciones[coleccion].append(carpeta)
			else:
				diccionarioColecciones[coleccion] = [carpeta]
		elif "_DSPACE" in libroExistente:
			logging.info("El libro "+libroExistente+" ya ha sido procesado en ocasiones pasadas")
			print "El libro "+libroExistente+" ya ha sido procesado en ocasiones pasadas"			
		else:
			logging.info("El libro "+libroExistente+" no existe en el archivo de metadatos")
			print "El libro "+libroExistente+" no existe en el archivo de metadatos"
	if diccionarioColecciones:
		return True, diccionarioColecciones
	else:
		return False, False

if __name__ == '__main__':
    main(sys.argv)


