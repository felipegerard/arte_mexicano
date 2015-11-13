# coding=utf-8
import luigi
import os
import sys
import inspect
import re
import shutil
import json

from pdf_creation_functions import *
from text_extraction import InputPDF

# Input PDF directory
class InputPDF(luigi.ExternalTask):
	filename = luigi.Parameter()
	def output(self):
		return luigi.LocalTarget(self.filename)

# Read raw text from PDF files and join them in a single .pdf that has lower than 50mb.
class JoinPDF(luigi.Task):
	'''Extraer texto de los PDFs de un libro,
	pegarlos en archivos menores de 50mb'''
	book_name = luigi.Parameter()		# Nombre del libro
	pdf_dir = luigi.Parameter() 		# Carpeta de PDFs
	full_pdf_dir = luigi.Parameter()	# Carpeta de PDFs completos

	def requires(self):
		pdf_bookdir = os.path.join(self.pdf_dir, self.book_name)
		return InputPDF(pdf_bookdir)

	def output(self):
		return luigi.LocalTarget(os.path.join(self.full_pdf_dir, self.book_name)) # ==> La salida cambió a la ruta full_pdf_dir
		
	def run(self):
		# Extraer textos
		ruta_pdfs = self.input().path
		lista_pdfs = [os.path.join(ruta_pdfs,x) for x in os.listdir(ruta_pdfs) if '.pdf' in x]
		
		# Si no existe la ruta del libro en full_pdf_dir, la creamos
		if not os.path.exists(os.path.join(self.full_pdf_dir, self.book_name)):
			os.makedirs(os.path.join(self.full_pdf_dir, self.book_name))

		# Generar y guardar extractos de texto
		# ==> Necesitamos que generar_libro use obtener_contenido_libro
		# ==> Necesitamos poderle dar la ruta de full_pdf_dir para que saque el libro ahí (full_pdf_dir/libro/cachos_50_megas)
		generar_libro(ruta_pdfs,lista_pdfs,self.output().path)
		

# Este proceso sirve para correr todos los JoinPDF de golpe y posiblemente en paralelo
class JoinPDFs(luigi.Task):
	pdf_dir = luigi.Parameter()
	full_pdf_dir = luigi.Parameter()
	meta_file = luigi.Parameter(default='libros_juntados.txt')

	def requires(self):
		return {book:JoinPDF(os.path.join(self.pdf_dir, book))
				for book in os.listdir(self.pdf_dir)}

	def output(self):
		return {book:luigi.LocalTarget(os.path.join(self.full_pdf_dir, self.book_name)
				for book in self.input().keys()} # Le basta saber que existe la carpeta. Se crea en el JoinPDF correspondiente
		
	def run(self):
		# Generamos metadatos. Este proceso es de chocolate y sirve nada más para correr todos los JoinPDF en el input
		joined_books = [d for d in os.listdir(self.full_pdf_dir) if self.meta_file not in d]
		with open(os.path.join(self.full_pdf_dir, self.meta_file), 'w') as f:
			f.write('\n'.join(joined_books))





















