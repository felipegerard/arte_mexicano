
# coding=utf-8
## ES IMPORTANTE INDICAR EL ENCODING

import luigi
import os
import inspect
import re
import pickle
import unicodedata
from gensim import corpora, models, similarities

# ----------------------------------------------------------------
# Funciones y clases adicionales

# Quitar caracteres con acentos
def remove_accents(input_str):
    if type(input_str) is not unicode:
        input_str = unicode(input_str, 'utf-8')
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

# Iterar sobre un corpus
class CorpusIterator(object):
    def __init__(self, dir):
        '''dir debe contener los documentos limpios'''
        self.dir = dir
        self.dir_list = os.listdir(self.dir)
    
    def __iter__(self):
        for doc in self.dir_list:
            f = open(self.dir + '/' + doc)
            d = f.read() #.decode('utf-8')
            f.close()
            yield d

# ----------------------------------------------------------------
# Data Flow

# Imports UNAM
try:
	from cStringIO import StringIO
except:
	from StringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from nltk import wordpunct_tokenize
from nltk.corpus import stopwords



# Input PDF
class InputPDF(luigi.ExternalTask):
	filename = luigi.Parameter()
	def output(self):
		return luigi.LocalTarget(self.filename)


# Limpiar texto ### FALTA

def clean_text(self, d):
	    '''d debe ser un string'''
	    d = remove_accents(d)
	    d = re.sub('\n', ' ', d)
	    d = d.lower()
	    d = re.sub('[^a-z0-9 ]', ' ', d)
	    d = re.sub(' +', ' ', d)
	    d = re.sub(' ([^ ]{1,3} )+', ' ', d, )
	    d = re.sub(' [^ ]*(.)\\1{2,}[^ ]* ', ' ', d)
	    return d

# Input book
execfile('functions/pdf2txt.py')

class ReadText(luigi.Task):
	pdf_bookdir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	meta_file = luigi.Parameter(default='librosAgregados.tm')

	def requires(self):
		return InputPDF(self.pdf_bookdir)
		
	def run(self):
		idioma, contenido = extraerVolumen(self.input())
		with self.output().open('w') as f:
			f.write(contenido)

		guardarMetadatos(self.input,idioma,self.txt_dir,self.meta_file)
	
	def output(self):
		book_name = os.path.split(self.input().path)[-1]
		outfile = os.path.join(self.txt_dir,'books',book_name+'.txt')
		return luigi.LocalTarget(outfile)

# Meter a carpetas de idioma. Si no hacemos esto entonces no es idempotente
import shutil
from pprint import pprint
class SortByLanguage(luigi.Task):
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	lang_file = luigi.Parameter(default='idiomas.tm')

	def requires(self):
		pdf_bookdirs = [os.path.join(self.pdf_dir, b) for b in os.listdir(self.pdf_dir)]
		return [ReadText(pdf_bookdir, self.txt_dir, self.meta_file)	for pdf_bookdir in pdf_bookdirs]
		
	def run(self):
		# Leer archivo de metadatos generado
		meta = self.txt_dir + '/' + self.meta_file
		with open(meta, 'r') as f:
			metadatos = f.read().split('\n')
		metadatos = {i.split('\t')[0]:i.split('\t')[1] for i in metadatos if i != ''}
		idiomas = list(set(metadatos.values()))
		
		# Crear carpetas de idioma
		for i in idiomas:
			print '--------------------'
			print 'Creando carpeta de ', i
			os.mkdir(self.txt_dir + '/' + i)

		# Mover archivos a sus carpetas
		print '---------------------------'
		for k,idioma in metadatos.iteritems():
			print k, ' --> ', idioma
			old = os.path.join(self.txt_dir, 'books', k + '.txt')
			new = os.path.join(self.txt_dir, idioma, k + '.txt')
			shutil.copyfile(old, new)

		# Metadatos de salida
		with self.output().open('w') as f:
			f.write('\n'.join(idiomas))
	
	def output(self):
		outfile = os.path.join(self.txt_dir, self.lang_file)
		return luigi.LocalTarget(outfile)



# Generar diccionario
execfile('functions/GeneradorDiccionario.py')
execfile('functions/GeneradorCorpus.py')
execfile('functions/TopicModeling.py')

class GenerateDictionary(luigi.Task):
	"""docstring for CleanText"""
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	model_dir = luigi.Parameter()
	meta_file = luigi.Parameter(default='librosAgregados.tm')
	lang_file = luigi.Parameter(default='idiomas.tm')
	min_docs_per_lang = luigi.IntParameter(default=1)
	
	idiomas = []

	def requires(self):
		return SortByLanguage(self.pdf_dir,
							  self.txt_dir,
							  self.meta_file,
							  self.lang_file)

	def output(self):
		return [luigi.LocalTarget(self.model_dir + '/diccionario_' + idioma + '.dict') for idioma in self.idiomas]
		# return luigi.LocalTarget(self.txt_dir + '/idiomas.txt')

	def run(self):
		idiomas_omitidos = ['swedish']
		lang_file = os.path.join(self.txt_dir, self.lang_file)
		with open(lang_file, 'r') as f:
			idiomas = f.read().split('\n')
			# idiomas = [i in idiomas if i not in idiomas_omitidos]
			print '======================='
			print idiomas

		self.idiomas = idiomas
		for idioma in idiomas:
			print '=========================='
			print 'Generando diccionario de ' + idioma

			rutaTextos = os.path.join(self.txt_dir,idioma)
			if len(os.listdir(rutaTextos)) < self.min_docs_per_lang:
				logging.info("No hay suficientes muestras para generar el modelo. Omitiendo idioma.")
				print "No hay suficientes muestras para generar el modelo. Omitiendo idioma."
				continue
			elif not os.path.exists(self.model_dir):
				print "Creando carpeta base para modelos."
				os.makedirs(self.model_dir)
			generarDiccionario(rutaTextos, self.model_dir, 6, idioma)
			#generarCorpus(rutaTextos, self.model_dir, 6, idioma)




# Generar diccionario
# execfile('functions/GeneradorDiccionario.py')
# execfile('functions/GeneradorCorpus.py')
# execfile('functions/TopicModeling.py')

# class GenerateDictionary(luigi.Task):
# 	"""docstring for CleanText"""
# 	pdf_dir = luigi.Parameter()
# 	txt_dir = luigi.Parameter()
# 	model_dir = luigi.Parameter()
# 	min_docs_per_lang = luigi.IntParameter(default=1)
# 	idiomas = []

# 	def requires(self):
# 		return ReadText(self.pdf_dir, self.txt_dir)	
	
# 	def run(self):
# 		idiomas_omitidos = ['swedish']
# 		idiomas = os.listdir(self.txt_dir)
# 		idiomas = [idioma for idioma in idiomas \
# 			if '.' not in idioma \
# 				and idioma not in idiomas_omitidos]
# 		self.idiomas = idiomas
# 		for idioma in idiomas:
# 			print '=========================='
# 			print 'Generando diccionario de ' + idioma
# 			rutaTextos = os.path.join(self.txt_dir,idioma)
# 			if len(os.listdir(rutaTextos)) < self.min_docs_per_lang:
# 				logging.info("No hay suficientes muestras para generar el modelo. Omitiendo idioma.")
# 				print "No hay suficientes muestras para generar el modelo. Omitiendo idioma."
# 				continue
# 			elif not os.path.exists(self.model_dir):
# 				print "Creando carpeta base para modelos."
# 				os.makedirs(self.model_dir)
# 			generarDiccionario(rutaTextos, self.model_dir, 6, idioma)
# 			#generarCorpus(rutaTextos, self.model_dir, 6, idioma)

# 		with open(self.txt_dir + '/idiomas.txt', 'w') as f:
# 			f.write('\n'.join(idiomas) + '\n')

# 	def output(self):
# 		return [luigi.LocalTarget(self.model_dir + '/diccionario_' + idioma + '.dict') for idioma in self.idiomas]
# 		#return luigi.LocalTarget(self.txt_dir + '/idiomas.txt')




# Corpus
class GenerateCorpus(luigi.Task):
	"""docstring for CleanText"""
	pdf_dir = luigi.Parameter()
	txt_dir = luigi.Parameter()
	model_dir = luigi.Parameter()
	min_docs_per_lang = luigi.IntParameter(default=1)
	idiomas = []

	def requires(self):
		return GenerateDictionary(self.pdf_dir, self.txt_dir, self.model_dir, self.min_docs_per_lang)	
	
	def run(self):
		idiomas_omitidos = ['swedish']
		idiomas = os.listdir(self.txt_dir)
		idiomas = [idioma for idioma in idiomas \
			if '.' not in idioma \
				and idioma not in idiomas_omitidos]
		self.idiomas = idiomas
		for idioma in idiomas:
			print '=========================='
			print 'Generando corpus en ' + idioma
			rutaTextos = os.path.join(self.txt_dir,idioma)
			generarCorpus(rutaTextos, self.model_dir, 6, idioma)

	def output(self):
		return [luigi.LocalTarget(self.model_dir + '/corpus_' + idioma + '.dict') for idioma in self.idiomas]


# class GenerateDictionary(luigi.Task):
# 	"""Docstring"""
# 	input_dir = luigi.Parameter()
# 	clean_dir = luigi.Parameter()
# 	model_dir = luigi.Parameter()

# 	def requires(self):
# 		return [CleanText(self.input_dir + '/' + i, self.clean_dir + '/' + i) for i in os.listdir(self.input_dir)]

# 	def run(self):
# 		if not os.path.exists(self.clean_dir):
# 			print "Creando carpeta base para archivos txt."
# 			os.makedirs(self.clean_dir)
# 		dictionary = corpora.Dictionary(doc.open('r').read().split() for doc in self.input())
# 		once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq <= 1]
# 		dictionary.filter_tokens(once_ids) # remove words that appear only once
# 		dictionary.compactify()
# 		f = self.output().open('w')
# 		pickle.dump(dictionary, f)
# 		f.close()

# 	def output(self):
# 		return luigi.LocalTarget(self.model_dir + '/' + 'dictionary.pickle')

class Vectorize(luigi.Task):
	"""Docstring"""
	input_dir = luigi.Parameter()
	clean_dir = luigi.Parameter()
	model_dir = luigi.Parameter()

	def requires(self):
		return GenerateDictionary(self.input_dir, self.clean_dir, self.model_dir)

	def run(self):
		with self.input().open('r') as f:
			dictionary = pickle.load(f)
		print dictionary
		corpus_iterator = CorpusIterator(self.clean_dir)
		corpus_bow = [dictionary.doc2bow(d.split()) for d in corpus_iterator]
		corpora.MmCorpus.serialize(self.model_dir + '/' + 'corpus.mmkt', corpus_bow)

	def output(self):
		return luigi.LocalTarget(self.model_dir + '/' + 'corpus.mmkt')

class TransformTFIDF(luigi.Task):
	"""Docstring"""
	input_dir = luigi.Parameter()
	clean_dir = luigi.Parameter()
	model_dir = luigi.Parameter()

	def requires(self):
		return Vectorize(self.input_dir, self.clean_dir, self.model_dir)

	def run(self):
		corpus = corpora.MmCorpus(self.model_dir + '/' + 'corpus.mmkt')
		tfidf_transform = models.TfidfModel(corpus)
		with self.output().open('w') as f:
			pickle.dump(tfidf_transform, f)

	def output(self):
		return luigi.LocalTarget(self.model_dir + '/' + 'tfidf_transform.pickle')

class DocumentSimilarities(luigi.Task):
	"""Docstring"""
	input_dir = luigi.Parameter()
	clean_dir = luigi.Parameter()
	model_dir = luigi.Parameter()
	num_sim_docs = luigi.IntParameter(default=5)

	def requires(self):
		return TransformTFIDF(self.input_dir, self.clean_dir, self.model_dir)

	def run(self):
		print 'Loading Transform'
		print '==========================='
		with self.input().open('r') as f:
			tfidf_transform = pickle.load(f)
		print 'Loading Corpus'
		print '==========================='
		corpus = corpora.MmCorpus(self.model_dir + '/' + 'corpus.mmkt')
		print 'Creating Index'
		print '==========================='
		index = similarities.MatrixSimilarity(tfidf_transform[corpus])
		#index.save(self.model_dir + '/' + 'index.pickle')

		print 'Calculating Similarities'
		print '==========================='
		sims = []
		i = 1
		for doc in corpus:
			i = i + 1
			print i
			doc_tfidf = tfidf_transform[doc]
			sim = sorted(enumerate(index[doc_tfidf]), key = lambda item: item[1], reverse=True)
			sims.append(sim[:self.num_sim_docs])
			#print sims[:self.num_sim_docs]
		with self.output().open('w') as f:
			pickle.dump(sims, f)

	def output(self):
		return luigi.LocalTarget(self.model_dir + '/' + 'similarities.pickle')


if __name__ == '__main__':
	luigi.run()











