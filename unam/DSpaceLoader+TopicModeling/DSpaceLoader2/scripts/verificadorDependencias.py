# -*- coding: utf-8 -*-
"""
#DSpaceLoader V2
/scripts/verificadorDependencias.py
#########
#	31/08/2015
#	Sistema desarrollado por el GIL, Instituto de Ingenieria UNAM
#	cgonzalezg@iingen.unam.mx
#	Verifica que las dependencias utilizadas por DSpaceLoader existan
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
		import openpyxl
	except ImportError, e:
		print "El módulo 'openpyxl' no está instalado. Es posible instalarlo utilizando el siguiente comando: 'sudo easy_install openpyxl'"
		bandera = False
		
	try:
		import PyPDF2
	except ImportError, e:
		print "El módulo 'PyPDF2' no está instalado. Es posible instalarlo utilizando el siguiente comando: 'sudo easy_install PyPDF2'"
		bandera = False

	try:
		import pdfminer
	except ImportError, e:
		print "El módulo 'pdfminer' no está instalado. Es posible instalarlo utilizando el siguiente comando: 'sudo easy_install pdfminer'"
		bandera = False

	return bandera

if __name__ == '__main__':
    main(sys.argv)