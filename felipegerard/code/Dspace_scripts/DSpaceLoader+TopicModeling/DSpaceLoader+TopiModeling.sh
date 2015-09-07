#!/bin/bash
#DSpaceLoader+TopicModeling.sh
#########
#	31/08/2015
#	Sistema desarrollado por el GIL, Instituto de Ingenieria UNAM
#	cgonzalezg@iingen.unam.mx
#########

#NOTA: La entrada al sistema debe ser única y exclusivamente a través de este script
CANTIDAD_LIBROS="0"
RUTA_WAREHOUSE="/export/librarian/"
NOMBRE_XLSX="/home/dspaceadmin/inventario.xlsx"
RUTA_GENERAL_LIBROS="/export/dspacearchive/libros"
EPERSON="carlos.fuentes@orcmx.com"
RUTA_BASE_TXTS="/export/dspacearchive/txt"
RUTA_LSI="/export/dspacearchive/lsi"
RUTA_XML="/home/dspaceadmin/dspace/webapps/xmlui/themes/Mirage/lib/xsl/aspect/artifactbrowser"
BD_USUARIO="dspace"
BD_PASSWORD="4)2;V>X"
URL_BASE="http://200.66.82.41:8080"
./DSpaceLoader2/DSpaceLoader.sh $CANTIDAD_LIBROS $RUTA_WAREHOUSE $NOMBRE_XLSX $RUTA_GENERAL_LIBROS $EPERSON
./TopicModeling1.1/TopicModeling.sh $RUTA_GENERAL_LIBROS $RUTA_BASE_TXTS $RUTA_LSI $RUTA_XML $BD_USUARIO $BD_PASSWORD $URL_BASE

