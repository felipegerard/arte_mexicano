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

class GenerateXML(luigi.Task):
	
	rutaXML = luigi.Parameter()
	lista_libros_similares = luigi.Parameter() 
	# Lista de similares por libro generado por el modelo
	# tiene que tener estrucura de lista de listas donde 
	# se tiene cada Libro con sus respectivos similares y respectiva simulitud
	
	#url_base = luigi.Parameter() #Parámetro para ellos para poder tener links en el DSPACE.
	
	def requires(self):
		return  #REQUIERE CORRER EL MODELO SHOW LSI para GENERAR EL JSON PARA LA LECTURA DE SIMILARES; NO SE BIEN CÓMO PASAR LOS PARÄMETROS

	def output(self):
		return luigi.LocalTarget(self.rutaXML)

	def run(self):
		ap = open(self.output(),"w")
		ap.write( extraerSimilares( self.lista_libros_similares ) )
		ap.close()
		print "XML finalizado!"
		
	


