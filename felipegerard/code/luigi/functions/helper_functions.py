


# ----------------------------------------------------------------
# Funciones y clases indispensables


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
import os
import io
import sys
import logging
import shutil
import unicodedata
import re

#from GeneradorDiccionario import GeneradorDiccionario
#from GeneradorCorpus import GeneradorCorpus

# execfile('functions/GeneradorDiccionario.py')
# execfile('functions/GeneradorCorpus.py')
# execfile('functions/GeneradorLSI.py')

# Generar diccionario

# def generarDiccionario(carpeta_textos, truncamiento, idioma):
#     generadorDiccionario = GeneradorDiccionario(carpeta_textos, truncamiento)
#     #FELIPE# listaArchivos = generadorDiccionario.obtenerLibros()
#     generadorDiccionario.generarDiccionario()
#     generadorDiccionario.serializarDiccionario(idioma)

# Generar corpus
# def generarCorpus(carpeta_textos, carpeta_salida, truncamiento, idioma):
#     generadorCorpus = GeneradorCorpus(carpeta_textos, carpeta_salida, truncamiento)
#     generadorCorpus.obtenerLibros()
#     generadorCorpus.generarCorpus(idioma)
#     generadorCorpus.serializarCorpus(idioma)

# ----------------------------------------------------------------
# Funciones y clases adicionales

def save_content(target_dir, book_name, content):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print '--------------------'
        print 'Creando carpeta ' + target_dir

    # Guardar contenido
    book_path = os.path.join(target_dir,book_name+'.txt')
    with open(book_path, 'w') as f:
        f.write(content)
    print book_name + ' --> ' + target_dir

# Limpiar texto ### FALTA

# Quitar caracteres con acentos
def remove_accents(input_str):
    if type(input_str) is not unicode:
        input_str = unicode(input_str, 'utf-8')
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

def clean_text(d):
        '''d debe ser un string'''
        d = remove_accents(d)
        d = re.sub('\n', ' ', d)
        d = d.lower()
        d = re.sub('[^a-z0-9 ]', ' ', d)
        d = re.sub(' +', ' ', d)
        d = re.sub(' ([^ ]{1,3} )+', ' ', d, )
        d = re.sub(' [^ ]*(.)\\1{2,}[^ ]* ', ' ', d)
        return d

def remove_stopwords(clean_text, lang):
    content = clean_text.split(' ')
    return ' '.join([w for w in content if w not in stopwords.words(lang)])

# Regresar similitudes
from gensim.similarities import Similarity
def arrange_similarities(index, file_list, num_sims=5):
    sims = []
    for i, idx in enumerate(index):
        s = []
        for j in range(len(file_list)):
            s.append((i,j,file_list[i],file_list[j],idx[j]))
        s = sorted(s, key = lambda item: item[4], reverse=True)
        sims += s
    return sims

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