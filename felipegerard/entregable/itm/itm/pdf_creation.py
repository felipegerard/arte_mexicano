# coding=utf-8
import luigi
import os
import sys
import inspect
import re
import shutil
import json

from pdf_creation_functions import *

# Input PDF directory
class InputPDF(luigi.ExternalTask):
	filename = luigi.Parameter()
	def output(self):
		return luigi.LocalTarget(self.filename)

# Read raw text from PDF files and join them in a single .pdf that has lower than 50mb.
class ReadPDF(luigi.Task):
	'''Extraer texto de los PDFs de un libro,
	pegarlos en archivos menores de 50mb'''
	book_name = luigi.Parameter()		# Nombre del libro
	pdf_dir = luigi.Parameter() 		# Carpeta de PDFs

	def requires(self):
		pdf_bookdir = os.path.join(self.pdf_dir, self.book_name)
		return InputPDF(pdf_bookdir)

	def output(self):
		return luigi.LocalTarget(os.path.join(self.pdf_dir, self.book_name,'pdf_full') )
		
	def run(self):
		# Extraer textos
		ruta_pdfs = self.input().path
		lista_pdfs = [os.path.join(rutaBase,x) for x in os.listdir(rutaBase) if '.pdf' in x]
		
		# Generar y guardar extractos de texto
		 generar_libro(ruta_pdfs,lista_pdfs,self.output())
		