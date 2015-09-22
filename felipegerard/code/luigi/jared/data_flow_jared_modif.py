import luigi
import os
import pickle
from scipy import misc
#from joblib import Parallel, delayed  
import multiprocessing
import csv
from collections import defaultdict
from pprint import pprint

class CarpetaLibro(luigi.ExternalTask):
	"""
	Todo empieza dando de alta la carpeta donde estan 
	todos los libros.
	"""
	input_dir = luigi.Parameter()

	def output(self):
		"""
		Solo va a regresar la existencia de la carpeta
		de la carpeta con todos los libros
		"""

		#El directorio donde viven todos los libros
		return luigi.LocalTarget(self.input_dir)
		

class IdentificarImagenes(luigi.Task):
	"""
	Se a toma el listado de los jpgs y se analiza
	si en esta pagina puede ver una pintura
	"""
	jpg_dir = luigi.Parameter() # Carpeta de jpgs (jpg/libro/pagina.jpg)
	output_file = luigi.Parameter(default='imagenes.csv') # Archivo de salida con info de imagenes

	def requires(self):
		return [CarpetaLibro(os.path.join(self.jpg_dir, x)) for x in os.listdir(self.jpg_dir)] # Nos volamos el proceso intermedio

	def output(self):		
		return luigi.LocalTarget(self.output_file)

	def run(self):

		# Nombres de todos los archivos
		libros = [libro.path for libro in self.input()]
		libros_jpgs = {}
		for libro in libros:
			try:
				libros_jpgs[libro]= os.listdir(libro)
			except:
				pass

		def rgb2gray(rgb):
			"""
			Convertir imagenes en escala de grises
			"""
			r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
			gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
			return gray

		# Diccionario {libro:[paginas con imagenes]}
		resultado = defaultdict(list) # Esto es para que por default los valores sean listas
		# i = 0
		for libro, jpgs_lib in libros_jpgs.iteritems():
			pprint(dict(resultado)) # Para ir viendo el avance del objeto
			# if i == 2:
			# 	break
			# else:
			# 	i += 1
			for jpg in jpgs_lib:
				ruta_jpg = os.path.join(libro,jpg)
				print ruta_jpg
				try:
					pagina = misc.imread(ruta_jpg)
					pagina = rgb2gray(pagina)
					if pagina.var()>5000:
						resultado[os.path.split(libro)[-1]].append(jpg)
				except:
					1
		"""Escribimos algo del tipo:
		libro1
		pag_con_imags_1.jpg
		pag_con_imags_4.jpg

		libro2
		pag_con_imags_3.jpg
		pag_con_imags_5.jpg
		pag_con_imags_5.jpg
		"""
		resultado = '\n\n'.join([k + '\n' + '\n'.join(v) for k,v in resultado.iteritems()])
		with self.output().open("w") as f:
			f.write(resultado)

		"""Para leer este resultado:
		with open('test/models/imagenes.txt', 'r') as f:
		    t = f.read()
		res = {j[0]:j[1:] for j in [i.split('\n') for i in t.split('\n\n')] if len(j) > 1}
		La ventaja es que también se puede abrir desde otros lados!"""

if __name__ == '__main__':
	luigi.run()