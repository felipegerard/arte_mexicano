


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

# ----------------------------------------------------------------
# Funciones y clases adicionales

# Limpiar texto ### FALTA

# Quitar caracteres con acentos
# def remove_accents(input_str):
#     if type(input_str) is not unicode:
#         input_str = unicode(input_str, 'utf-8')
#     nkfd_form = unicodedata.normalize('NFKD', input_str)
#     return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


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