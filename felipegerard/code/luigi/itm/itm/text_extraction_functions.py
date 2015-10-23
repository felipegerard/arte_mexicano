# coding=utf-8

import os
import io
import sys
import logging
import shutil

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

def obtener_rutas(rutaBase, extension='.pdf', blacklist=None):
	if blacklist is None:
	    return [os.path.join(rutaBase,x) for x in os.listdir(rutaBase) if extension in x]
	else:
		return [os.path.join(rutaBase,x) for x in os.listdir(rutaBase) if (extension in x) and (x not in blacklist)]

def calcularValoresDeIdioma(contenido):
    languages_ratios = {}
    tokens = wordpunct_tokenize(contenido)
    words = [word.lower() for word in tokens]
    for language in stopwords.fileids():
        stopwords_set = set(stopwords.words(language))
        words_set = set(words)
        common_elements = words_set.intersection(stopwords_set)
        languages_ratios[language] = len(common_elements)
    return languages_ratios

def detectarIdioma(contenido):
    valores = calcularValoresDeIdioma(contenido)
    idioma = max(valores, key=valores.get)
    return idioma

def convertir(rutaVolumen, hojas=None):
    if not hojas:
        hojas = set()
    else:
        hojas = set(hojas)
    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)
    infile = file(rutaVolumen, 'rb')
    for hoja in PDFPage.get_pages(infile, hojas):
        interpreter.process_page(hoja)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text

def convertirVolumenes(rutaVolumenes):
    txt = ""
    for rutaVolumen in rutaVolumenes:
        try:
            txt += convertir(rutaVolumen)
        except Exception:
            logging.info("ERROR al convertir el volumen "+rutaVolumen)
            print "ERROR al convertir el volumen "+rutaVolumen
    return txt

def extraerVolumen(inputPDF):
    print "---------------------------------"
    print "Convirtiendo "+inputPDF.path
    rutaVolumenes = obtener_rutas(inputPDF.path, '.pdf')
    contenido = convertirVolumenes(rutaVolumenes)
    idioma = detectarIdioma(contenido)
    return idioma, contenido

# Guardar metadatos
def guardarMetadatos(book_name,idioma,txt_dir,meta_file):
    outfile = book_name
    meta = os.path.join(txt_dir, meta_file)
    flag = True
    if os.path.exists(meta):
        with open(meta, 'r') as f:
            log = f.read()
            if outfile in log:
                flag = False
    if flag:
        with open(meta, 'a+') as f:
            f.write(outfile + '\t'+ idioma + '\n')

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


def get_extracts(string, min_length=500, percentages=[0.1,0.5,0.9], max_start_offset=10, max_lines=20):
    str_list = string.split('\n')
    positions = [int(p*len(str_list)) for p in percentages]
    extracts = []

    for p in positions:
        s = ''
        for i in range(p, min(p + max_start_offset, len(str_list)-1), 1):
            if len(str_list[i]) > 0 and str_list[i][0].isupper():
                break
            p = p + 1
        for i in range(p, min(p + max_lines, len(str_list)-1), 1):
            if len(s) >= min_length:
                break
            else:
                s += '\n' + str_list[i]
        extracts.append({'start_line':p, 'start_line_perc':round(1.0*p/len(str_list),3), 'text':s})
    return extracts








