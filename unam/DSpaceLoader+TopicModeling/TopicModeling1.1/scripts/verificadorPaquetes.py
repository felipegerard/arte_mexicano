# -*- coding: utf-8 -*-
"""
#TopicModeling V2
/scripts/verificadorPaquetes.py
#########
#	02/08/2015
#	Sistema desarrollado por el GIL, Instituto de Ingenieria UNAM
#	cgonzalezg@iingen.unam.mx
#	Verifica que las dependencias utilizadas por TopicModeling existan
#	return:
#		True -> si todas las dependencias están instaladas
#		False -> si falta alguna dependencia
#########
"""
import sys

def main(args):	
	if args[0] != "":
		print "NO ES POSIBLE EJECUTAR EL SCRIPT. FAVOR DE UTILIZAR DSpaceLoader.sh"
		return False

	bandera = True
	
	try:
		import pdfminer
	except ImportError, e:
		print "El módulo 'pdfminer' no está instalado. Es posible instalarlo utilizando el siguiente comando: 'sudo easy_install pdfminer'"
		bandera = False

	try:
		import gensim
	except ImportError, e:
		print "El módulo 'gensim' no está instalado. Es posible instalarlo utilizando el siguiente comando: 'sudo easy_install gensim'"
		bandera = False

	try:
		import nltk
	except ImportError, e:
		print "El módulo 'nltk' no está instalado. Es posible instalarlo utilizando el siguiente comando: 'sudo easy_install nltk'"
		bandera = False

	return bandera

if __name__ == '__main__':
    main(sys.argv)