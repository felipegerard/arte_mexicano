import luigi
import os
import pickle
from scipy import misc
from joblib import Parallel, delayed  
import multiprocessing
import csv

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
		

class ListadoLibrosJpgs(luigi.Task):
	"""
	Este proceso va a crear un listado con los nombres de 
	todos los libros en un diccionario
	"""
	input_dir = luigi.Parameter()

	def requires(self):
		return [CarpetaLibro(os.path.join(self.input_dir, x)) for x in os.listdir(self.input_dir)]
	
	def output(self):
		return luigi.LocalTarget('libros_jpgs.pickle')

	def run(self):
		
		libros = [libro.path for libro in self.input()]

		libros_jpgs = {}
		for libro in libros:
			try:
				libros_jpgs[libro]= os.listdir(libro + "/jpg" )
			except:
				pass

		f = self.output().open('w')
		pickle.dump(libros_jpgs, f)
		f.close()

class IdentificarImagenes(luigi.Task):
	"""
	Se a toma el listado de los jpgs y se analiza
	si en esta pagina puede ver una pintura
	"""
	input_dir = luigi.Parameter()

	def requires(self):
		return ListadoLibrosJpgs(self.input_dir)

	def output(self):		
		return luigi.LocalTarget('imagenes.csv')

	def run(self):

		def rgb2gray(rgb):
			"""
			Convertir imagenes en escala de grises
			"""
			r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
			gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
			return gray
		
		file_pickle = open(self.input().path)
		libros_dicc = pickle.load(file_pickle)
		file_pickle.close()

		resultado = []
		#Creamos la ruta para cada jpg
		for libro in libros_dicc.keys():
			jpgs_lib = libros_dicc[libro]
			for jpg in jpgs_lib:
				ruta_jpg = os.path.join(libro,"jpg",jpg)
				#abrimos cada jpg y checamos su varianza, si es alta la guardamos
				pagina = misc.imread(ruta_jpg)
				pagina = rgb2gray(pagina)
				if pagina.var()>5000:
					resultado.append(ruta_jpg)
		
		with open(self.output().path, "w") as output:
			writer = csv.writer(output, lineterminator='\n')
			for val in resultado:
				writer.writerow(val)

if __name__ == '__main__':
	luigi.run()