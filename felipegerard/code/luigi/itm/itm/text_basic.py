# coding=utf-8
import luigi
import os
import sys
import inspect
import re
import pickle
import unicodedata
import shutil

from textract import *
from textclean import clean_text, remove_stopwords, remove_accents

# Input PDF directory
class InputPDF(luigi.ExternalTask):
	filename = luigi.Parameter()
	def output(self):
		return luigi.LocalTarget(self.filename)

# Extract raw text
class ReadText(luigi.Task):
	'''Extraer texto de los PDFs de un libro,
	pegarlos en un solo archivo en formato crudo
	y guardar el resultado'''
	book_name = luigi.Parameter()		# Nombre del libro
	pdf_dir = luigi.Parameter() 		# Carpeta de PDFs
	txt_dir = luigi.Parameter()			# Carpeta de textos
	#jpg_dir = luigi.Parameter()			# Carpeta de JPGs
	#image_meta_dir = luigi.Parameter()	# Carpeta con archivos de metadatos para definir qué archivos son imágenes
	meta_dir = luigi.Parameter(default='meta')	# Nombre del archivo de metadatos
	meta_file = luigi.Parameter(default='librosAgregados.tm') # Nombre del archivo de metadatos libro-idioma

	def requires(self):
		pdf_bookdir = os.path.join(self.pdf_dir, self.book_name)
		return InputPDF(pdf_bookdir)

	def output(self):
		return luigi.LocalTarget(os.path.join(self.txt_dir,self.meta_dir,self.book_name+'.meta'))
		
	def run(self):
		# Extraer textos
		ruta_pdfs = self.input().path
		rutaVolumenes = obtener_rutas(ruta_pdfs, extension='.pdf')
		contenido = convertirVolumenes(rutaVolumenes)
		idioma = detectarIdioma(contenido)
		lang_path = os.path.join(self.txt_dir,idioma)
		save_content(lang_path, self.book_name, contenido)

		# Guardar los metadatos
		with self.output().open('w') as f:
			f.write(idioma)
		guardarMetadatos(self.book_name,idioma,
			os.path.join(self.txt_dir),self.meta_file)

# Clean text
class CleanText(luigi.Task):
	'''Limpiar el texto de un libro según el nivel de limpieza deseado
	y guardarlo en su carpeta correspondiente'''
	book_name = luigi.Parameter()
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	# jpg_dir = luigi.Parameter()
	# image_meta_dir = luigi.Parameter()
	meta_dir = luigi.Parameter(default='meta')
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	clean_level = luigi.Parameter(default='raw,clean,stopwords') # Nivel de limpieza. Cualquier combinación de 'raw', 'clean' y 'stopwords', separados por comas

	def requires(self):
		return ReadText(book_name = self.book_name,
						pdf_dir = self.pdf_dir,
						txt_dir = os.path.join(self.txt_dir, 'raw'),
						# jpg_dir = self.jpg_dir,
						# image_meta_dir = self.image_meta_dir,
						meta_dir = self.meta_dir,
						meta_file = self.meta_file)

	def output(self):
		flags = self.clean_level.split(',')
		if not ('raw' in flags or 'clean' in flags):
			print 'WARNING: No cleaning flags defined. Defaulting to raw format only...'
			flags = ['raw']
		metafiles = {kind:os.path.join(self.txt_dir,kind,'meta',self.book_name+'.meta')
					for kind in flags}
		return {kind:luigi.LocalTarget(path)
				for kind, path in metafiles.iteritems()}
		
	def run(self):
		flags = self.output().keys()
		if flags == ['raw']:
			print 'No hacemos limpieza de %s' % (self.book_name)

		# Leemos el idioma de los metadatos
		with self.input().open('r') as f:
			idioma = f.read()
		if 'clean' in flags:
			# Leemos el contenido crudo
			with open(os.path.join(self.txt_dir,'raw',idioma,self.book_name+'.txt'), 'r') as f:
				contenido = f.read()
			contenido = clean_text(contenido)
			lang_path = os.path.join(self.txt_dir,'clean',idioma)
			save_content(lang_path, self.book_name, contenido)
			if 'stopwords' in flags:
				contenido = remove_stopwords(contenido, idioma)
				lang_path = os.path.join(self.txt_dir,'stopwords',idioma)
				save_content(lang_path, self.book_name, contenido)
		elif 'stopwords' in flags:
			print 'WARNING: Cannot remove stopwords without cleaning first. Ommiting "stopwords" flag.'
		
		# Guardar los metadatos
		for kind, o in self.output().iteritems():
			with o.open('w') as f:
				f.write(idioma)
			guardarMetadatos(self.book_name,idioma,
				os.path.join(self.txt_dir,kind),self.meta_file)
	

# Detect languages and write language metadata. Possibly obsolete
class DetectLanguages(luigi.Task):
	'''Detectar idiomas de los libros y escribir archivo
	con los nombres de todos los idiomas detectados'''
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	# jpg_dir = luigi.Parameter()
	# image_meta_dir = luigi.Parameter()
	meta_dir = luigi.Parameter(default='meta')
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	lang_file = luigi.Parameter(default='idiomas.tm')
	clean_level = luigi.Parameter(default='raw,clean,stopwords')

	def requires(self):
		return [CleanText(book_name=book_name,
						  pdf_dir=self.pdf_dir,
						  txt_dir=self.txt_dir,
						  # jpg_dir = self.jpg_dir,
						  # image_meta_dir = self.image_meta_dir,
						  meta_dir=self.meta_dir,
						  meta_file=self.meta_file,
						  clean_level=self.clean_level)
				for book_name in os.listdir(self.pdf_dir)]

	def output(self):
		flags = self.input()[0].keys()
		metapath = os.path.join(self.txt_dir,self.lang_file)
		return {
					'langs':{
						kind:luigi.LocalTarget(os.path.join(self.txt_dir,kind,self.lang_file))
						for kind in flags
					},
					'files':self.input()
				}
		
	def run(self):
		for kind, target in self.output()['langs'].iteritems():
			idiomas = set()
			txt_kind_meta_dir = os.path.join(self.txt_dir,kind,self.meta_dir)
			for p in os.listdir(txt_kind_meta_dir):
				p = os.path.join(txt_kind_meta_dir, p)
				with open(p, 'r') as f:
					idiomas.add(f.read())
			idiomas = list(idiomas)
			# Metadatos de salida
			with target.open('w') as f:
				f.write('\n'.join(idiomas))