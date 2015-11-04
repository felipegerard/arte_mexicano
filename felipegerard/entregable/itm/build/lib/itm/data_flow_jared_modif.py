# coding=utf8
import luigi
import os
import pickle
from scipy import misc
#from joblib import Parallel, delayed  
import multiprocessing
import csv
from collections import defaultdict
from pprint import pprint

from skimage.filters import gaussian_filter
from skimage.color import rgb2gray

# def rgb2gray(rgb):
# 	"""
# 	Convertir imagenes en escala de grises
# 	"""
# 	r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
# 	gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
# 	return gray

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
	book_name = luigi.Parameter()
	jpg_dir = luigi.Parameter() # Carpeta de jpgs (jpg/libro/pagina.jpg)
	output_dir = luigi.Parameter() # Archivo de salida con info de imagenes
	varianza = luigi.FloatParameter(default=0.05)

	def requires(self):
		return CarpetaLibro(os.path.join(self.jpg_dir, self.book_name))

	def output(self):		
		return luigi.LocalTarget(os.path.join(self.output_dir, self.book_name + '.images'))

	def run(self):
		if not os.path.exists(self.output_dir):
			os.makedirs(self.output_dir)
			print 'USER INFO: Creando carpeta de listas de archivos con imágenes en ' + self.output_dir
		jpgs_lib = os.listdir(self.input().path)
		resultado = []
		for jpg in jpgs_lib:
			ruta_jpg = os.path.join(self.input().path,jpg)
			print '====================='
			print 'USER INFO: ' + ruta_jpg
			try:
				pagina = misc.imread(ruta_jpg)
				pagina = rgb2gray(pagina)
				pagina = gaussian_filter(pagina,sigma=2) #Un filtro que me de un promedio de la imagen
				if pagina.var() > self.varianza:
					resultado.append(jpg.replace('.jpg',''))
				print 'USER INFO: Var = ', pagina.var()
				print '====================='
				# resultado.append('basura')
			except:
				print 'USER WARNING: No se pudo leer la imagen ' + ruta_jpg

		resultado = '\n'.join(resultado)
		with self.output().open("w") as f:
			f.write(resultado)


# if __name__ == '__main__':
	# luigi.run()