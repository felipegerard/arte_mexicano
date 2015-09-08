# -*- coding: utf-8 -*-
"""
#DSpaceLoader V2
/scripts/cargadorPaquetes.py
#########
#	31/08/2015
#	Sistema desarrollado por el GIL, Instituto de Ingenieria UNAM
#	cgonzalezg@iingen.unam.mx
#	return: 
#########
"""

import os
from datetime import datetime
from subprocess import check_output
import logging
import io

def obtener_paquetes_terminados(carpeta_salida_libros):	

	return [os.path.join(carpeta_salida_libros,x) for x in os.listdir(carpeta_salida_libros) if "_DSPACE" in x]


def obtener_coleccion(carpeta_base):
	coleccion = ""
	try:
		ap = open(os.path.join(carpeta_base,"coleccion"),"r")
		coleccion = ap.read().replace("\n","")
		print "Colección "+coleccion
		logging.info("Colección "+coleccion)
		ap.close()
	except Exception:
		print "Error al leer la colección del libro. Omitiendo libro."
		logging.info("Error al leer la colección del libro. Omitiendo libro.")
	return coleccion

def verificar_en_registro(ruta_paquete):
	bandera = True
	try:
		ap = open("librosCargados.dsl","r")
		contenido = ap.readlines()
		if ruta_paquete+"\n" in contenido:
			bandera = True
		else:
			bandera = False
		ap.close()
		return bandera
	except Exception:
		print "El registro de libros aún no existe."
		logging.info("El registro de libros aún no existe.")
		return False
def agregar_en_registro(ruta_paquete):
	ap = open("librosCargados.dsl","a+")
	ap.write(ruta_paquete+"\n")
	ap.close()

def indexar_dspace():
	comando = "/home/dspaceadmin/dspace/bin/dspace filter-media"
	print "Indexando DSpace"
	logging.info("Indexando DSpace")
	respuesta = os.system(comando)
	if respuesta == 0:
		print "Se ha indexado DSpace correctamente."
		logging.info("Se ha indexado DSpace correctamente.")
		return True
	else:
		print "Error al indexar DSpace: "+str(respuesta)
		logging.info("Error al indexar DSpace: "+str(respuesta))
		return False

def cargar_paquete(carpeta_base, coleccion, eperson):
	nombre_mapfile = "./mapfiles/"+datetime.now().isoformat()	
	carpeta_base_m = carpeta_base.replace("&","\&").replace("(","\(").replace(")","\)").replace("`","\`")
	comando = "/home/dspaceadmin/dspace/bin/dspace import --add --eperson="+eperson+" --source="+carpeta_base_m+" --collection="+coleccion+" --mapfile="+nombre_mapfile

	print "Borrando archivo de coleccion..."
	logging.info("Borrando archivo de coleccion...")	
	os.remove(os.path.join(carpeta_base,"coleccion"))
	print "sudo "+comando
	respuesta = os.system(comando)	
	
	if respuesta == 0:
		print "Libro agregado exitósamente."
		logging.info("Libro agregado exitósamente.")
		agregar_en_registro(carpeta_base)
		return True
	else:
		print "Error al cargar el paquete: "+str(respuesta)
		print "Creando archivo de colección."
		logging.info("Error al cargar el paquete: "+str(respuesta))
		logging.info("Creando archivo de colección.")
		ap = open(os.path.join(carpeta_base,"coleccion"),"w")
		ap.write(coleccion)
		ap.close()
		return False

def cargar_paquetes(carpetas_base_libros, paquetes_no_cargados, eperson):
	i = 1
	for carpeta_base in carpetas_base_libros:
		print "Procesando paquete "+str(i)+"/"+str(len(carpetas_base_libros))+" "+carpeta_base
		logging.info("Procesando paquete "+str(i)+"/"+str(len(carpetas_base_libros))+" "+carpeta_base)
		if verificar_en_registro(carpeta_base):
			print "El paquete "+carpeta_base+" ya ha sido cargado."
			logging.info("El paquete "+carpeta_base+" ya ha sido cargado.")
			paquetes_no_cargados.append(carpeta_base)
		else:
			coleccion = obtener_coleccion(carpeta_base)
			if coleccion != "":
				if not cargar_paquete(carpeta_base, coleccion, eperson):
					paquetes_no_cargados.append(carpeta_base)
			else:
				paquetes_no_cargados.append(carpeta_base)
		i += 1
	print "Se han procesado todos los paquetes."	
	logging.info("Se han procesado todos los paquetes.")
	

def main(args):	
	if args[0] != "":
		print "NO ES POSIBLE EJECUTAR EL SCRIPT. FAVOR DE UTILIZAR DSpaceLoader.sh"
		return False
	
	carpeta_salida_libros = args[1]
	eperson = args[2]
	paquetes_no_cargados = list()


	carpetas_base_libros = obtener_paquetes_terminados(carpeta_salida_libros)
	cargar_paquetes(carpetas_base_libros, paquetes_no_cargados, eperson)
	indexar_dspace()
	return paquetes_no_cargados


if __name__ == '__main__':

    main(sys.argv)
