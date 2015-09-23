import luigi
import os
import pickle
from scipy import misc
from joblib import Parallel, delayed  
import multiprocessing
import csv
import re
import shutil
import skimage.io as io
from skimage.color import rgb2gray
from skimage.filters import gaussian_filter


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
	input_dir = luigi.Parameter()
	carpeta_lib = luigi.Parameter()
	output_dir = luigi.Parameter(default = 'Salidas')
	varianza = luigi.FloatParameter(default=0.05)
	
	def requires(self):
		return CarpetaLibro(os.path.join(self.input_dir, self.carpeta_lib))

	def output(self):		
		return luigi.LocalTarget(os.path.join(self.output_dir,self.carpeta_lib + ".csv"))

	def run(self):
		if not os.path.exists(self.output_dir):
			os.makedirs(self.output_dir)
			print 'USER INFO: Creando carpeta de listas de archivos con imagenes en ' + self.output_dir
		
		list_jpgs = os.listdir(os.path.join(self.input().path, "jpg"))

		resultado = []		
		for jpg in list_jpgs:
			try:
				#Creamos la ruta para cada jpg
				ruta_jpg = os.path.join(self.input().path,"jpg",jpg)
				#abrimos cada jpg y checamos su varianza, si es alta la guardamos
				pagina = io.imread(ruta_jpg)
				pagina = rgb2gray(pagina)
				pagina = gaussian_filter(pagina,sigma=2) #Un filtro que me de un promedio de la imagen
				if pagina.var() > self.varianza:
					resultado.append(ruta_jpg)
			except:
				print "Error al abrir el archivo" + self.input().path + jpg
				
		
		resultado = '\n'.join(resultado)
		with self.output().open("w") as f:
			f.write(resultado)

class CopiarTodasImagenes(luigi.Task):
	"""
	Este proceso va a hacer una copia de la pintura a otra carpeta
	"""
	input_dir = luigi.Parameter()
	carpeta_lib = luigi.Parameter()
	output_dir = luigi.Parameter(default = 'Salidas')
	varianza = luigi.FloatParameter(default=0.05)
	output_dir_imag = luigi.Parameter(default = 'Imagenes')

	def requires(self):
		return [IdentificarImagenes(self.input_dir,x) for x in os.listdir(self.input_dir)]
	
	def output(self):
		directorio_salida = os.path.join(self.output_dir, self.output_dir_imag)
		try:
			imagenes = []
			for book in self.input():
				with open(book.path, 'rb') as csvfile:
					leer = csv.reader(csvfile, delimiter=' ', quotechar='\n')
					for row in leer:
						imagenes.append(row)

			return [luigi.LocalTarget(os.path.join(directorio_salida,re.split("/",doc[0])[-1])) for doc in imagenes]
		except:
			return luigi.LocalTarget(os.path.join(directorio_salida,"dummy.csv"))

	def run(self):
		imagenes = []
		for book in self.input():
			with open(book.path, 'rb') as csvfile:
				leer = csv.reader(csvfile, delimiter=' ', quotechar='\n')
				for row in leer:
					imagenes.append(row)

		directorio_salida = os.path.join(self.output_dir, self.output_dir_imag)
		if not os.path.exists(directorio_salida):
			os.makedirs(os.path.join(self.output_dir, self.output_dir_imag))
			print 'USER INFO: Creando carpeta de listas de archivos con imagenes en ' + self.output_dir_imag

		for imagen in imagenes:
			shutil.copy2(imagen[0], directorio_salida)





class CopiarUnaImagen(luigi.Task):
	"""
	Este proceso va a hacer una copia de la pintura a otra carpeta
	"""
	input_dir = luigi.Parameter()
	carpeta_lib = luigi.Parameter()
	output_dir = luigi.Parameter(default = 'Salidas')
	varianza = luigi.FloatParameter(default=0.05)
	output_dir_imag = luigi.Parameter(default = 'Imagenes')

	def requires(self):
		return IdentificarImagenes(self.input_dir,self.carpeta_lib)
	
	def output(self):
		directorio_salida = os.path.join(self.output_dir, self.output_dir_imag)

		try:
			imagenes = []
			with open(self.input().path, 'rb') as csvfile:
				leer = csv.reader(csvfile, delimiter=' ', quotechar='\n')
				for row in leer:
					imagenes.append(row)

			return [luigi.LocalTarget(os.path.join(directorio_salida,re.split("/",doc[0])[-1])) for doc in imagenes]
		except:
			return luigi.LocalTarget(os.path.join(directorio_salida,"dummy.csv"))

	def run(self):
		imagenes = []
		with open(self.input().path, 'rb') as csvfile:
			leer = csv.reader(csvfile, delimiter=' ', quotechar='\n')
			for row in leer:
				imagenes.append(row)

		directorio_salida = os.path.join(self.output_dir, self.output_dir_imag)
		if not os.path.exists(directorio_salida):
			os.makedirs(os.path.join(self.output_dir, self.output_dir_imag))
			print 'USER INFO: Creando carpeta de listas de archivos con imagenes en ' + self.output_dir_imag

		for imagen in imagenes:
			shutil.copy2(imagen[0], directorio_salida)

class CopiarImagenesReducir(luigi.Task):
	"""
	Este proceso va a crear un listado con los nombres de 
	todos los libros en un diccionario
	"""
	input_dir = luigi.Parameter()

	def requires(self):
		return CopiarImagenes(self.input_dir)
	
	def output(self):
		imagenes = []
		with open(self.input().path, 'rb') as csvfile:
			leer = csv.reader(csvfile, delimiter=' ', quotechar='\n')
			for row in leer:
				imagenes.append(row)

		return [luigi.LocalTarget(os.path.join(re.split("/",doc[0])[0],"Imagenes",re.split("/",doc[0])[-1])) for doc in imagenes]

	def run(self):
		imagenes = []
		with open(self.input().path, 'rb') as csvfile:
			leer = csv.reader(csvfile, delimiter=' ', quotechar='\n')
			for row in leer:
				imagenes.append(row)
		
		for imagen in imagenes:
			shutil.copy2(imagen[0], self.input_dir + "/Imagenes")

if __name__ == '__main__':
	luigi.run()