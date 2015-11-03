
# coding=utf-8
## ES IMPORTANTE INDICAR EL ENCODING

import luigi
import os
import sys
import inspect
import re
import pickle
import unicodedata
#from gensim import corpora, models, similarities

import shutil
from pprint import pprint

from gensim import corpora
from gensim.models.ldamodel import LdaModel
from gensim.similarities import Similarity

#from GeneradorDiccionario import GeneradorDiccionario


# ----------------------------------------------------------------
# Data Flow

from text_basic import InputPDF, ReadText, CleanText, DetectLanguages
from dict_corp import GenerateDictionary, GenerateCorpus
from lda import TrainLDA, PredictLDA, ShowLDA
from lsi import TrainLSI, GroupByLSI












