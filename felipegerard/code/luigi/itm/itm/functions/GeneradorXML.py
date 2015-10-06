# -*- coding: utf-8 -*-
"""
#TopicModeling V1.1
/scripts/GeneradorXML.py
#########
#	02/08/2015
#	Sistema desarrollado por el GIL, Instituto de Ingenieria UNAM
#	cgonzalezg@iingen.unam.mx

#########
"""
import os
import io
import json
from subprocess import check_output
import logging

class GeneradorXML(object):
	def __init__(self, rutaXML, similaresTodos,bd_usuario,bd_password,url_base):
		self.rutaXML = rutaXML
		self.similares = similaresTodos
		self.bd_usuario = bd_usuario
		self.bd_password = bd_password
		self.url_base = url_base
		self.textoSimilares = ""
		logging.info("GeneradorXML creado.")
		print "GeneradorXML creado."

	def consultar(self,nombre):
		os.putenv("PGPASSWORD", self.bd_password)
		consulta = "-c SELECT row_to_json(row(text_value)) FROM metadatavalue WHERE resource_id IN (SELECT resource_id FROM metadatavalue where lower(text_value) like '"+nombre.replace("_"," ")+"' LIMIT 1) AND metadata_field_id = 25"
		respuesta =check_output(["psql","-t","-w","-U"+self.bd_usuario, "-ddspace", consulta])
		if "f1" in respuesta:
			return str(int(json.loads(respuesta)["f1"].split("/")[-1]))
		else:
			return "NULL"

	def generarSeccion(self, libro, listaSimilares):
		#self.url = http://200.66.82.41:8080
		url_base = self.url_base
		cadena = "\n\t<libro handle=\"123456789/"+self.consultar(libro)+"\">"
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

	def extraerSimilares(self):
		contenido = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n\n<similitud>"
		#print self.similares
		for libro in self.similares:
			listaSimilares = list()
			similares = self.similares[libro]
			for nombre,similitud in similares:
				if nombre != libro and similitud >= 0.5: #FELIPE# Desechar documentos con menos de 0.5 de similitud
					listaSimilares.append((nombre,self.consultar(nombre)))
			contenido += self.generarSeccion(libro,listaSimilares)
		contenido += "</similitud>"

		self.textoSimilares = contenido

	def escribirXML(self):
		ap = open(os.path.join(self.rutaXML,"archivoSimilitud.xml"),"w")
		ap.write(self.textoSimilares)
		ap.close()
		print "XML finalizado!"
		logging.info("XML finalizado")
		return True


