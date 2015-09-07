DSpaceLoader+TopicModeling
31/08/2015
Sistema desarrollado por el GIL, Instituto de Ingeniería UNAM
Contacto:
	Carlos González Gallardo
	cgonzalezg@iingen.unam.mx

+---INFORMACIÓN---+
*DSpaceLoader+TopicModeling está diseñado para correr en sistemas Unix o similares, ha sido probado en distribuciones Linux (Ubuntu y OpenSuse) así como en Apple OS X Yosemite.
*DSpaceloader+TopicModeling agrupa dos sistemas: DSpaceloader V2 y TopicModeling V1.1. 
*DSpaceloader+TopicModeling utiliza los sistemas mencionados para automatizar la carga de libros a DSpace realizado por DSpaceLoader V2 y el análisis de similitud semántico realizado por TopicModeling V1.1. 

+---REQUISITOS MÍNIMOS DEL SISTEMA---+
DSpaceLoader+TopicModeling está compuesto por un conjunto de scripts de Python; por lo que el intérprete de pyton 2.7 debe estar instalado en el sistema.
El uso del procesador y memoria RAM así como de Disco Duro depende totalmente de la cantidad de libros a procesar.

+---DEPENDENCIAS---+
DSpaceLoader+TopicModeling no utilza bibliotecas externas. Favor de revisar los archivos README.txt de DSpaceloader V2 y TopicModeling V1.1 para ver las dependencias particulares.

+---EJECUCIÓN---+
La ejecución de DSpaceLoader+TopicModeling se hace mediante el script llamado "DSpaceLoader+TopicModeling.sh", éste es necesario que cuente con permisos de ejecución. 
ES IMPORTANTE EJECUTAR DSpaceLoader+TopicModeling CON PERMISOS DE SUPERUSUARIO. DE LO CONTRARIO NO SERÁ POSIBLE INTERACTUAR CON DSpace.
DSpaceLoader+TopicModeling no recibe parámetros por línea de comandos. Los parámetros se encuentran definidos dentro del mismo script "DSpaceLoader+TopicModeling.sh". Estos parámetros son enviados a DSpaceLoader V2 y TopicModeling V1.1.

-PARÁMETROS-
Los 11 parámetros descrito a continuación son OBLIGATORIOS para DSpaceLoader+TopicModeling y se encuentran definidos en "DSpaceLoader+TopicModeling.sh".

CANTIDAD_LIBROS:	Cantidad de libros a procesar. 0: TODOS LOS LIBROS DISPONIBLES EN EL ARCHIVO DE METADATOS
			Ej: "500"
RUTA_WAREHOUSE:		Carpeta o dirección del warehouse
			Ej: "/export/librarian"
NOMBRE_XLSX:		Archivo de metadatos
			Ej: "/home/dspaceadmin/DSpaceLoader+TopicModeling/inventarioNvo.xlsx"
RUTA_GENERAL_LIBROS:	Carpeta en donde se colocarán los libros
			Ej: "/export/dspacearchive/libros"
EPERSON:		Eperson que será utilizado en DSpace
			Ej: "carlos.fuentes@orcmx.com"
RUTA_BASE_TXTS:		Carpeta en donde se colocarán los libros en txt
			Ej: "/export/dspacearchive/txt"
RUTA_LSI:		Carpeta en donde se almacenarán las estructuras de LSI
			Ej: "/export/dspacearchive/lsi"
RUTA_XML:		Carpeta en donde se colocará el archivo xml
			Ej: "/home/dspaceadmin/dspace/webapps/xmlui/themes/Mirage/lib/xsl/aspect/artifactbrowser"
BD_USUARIO:		Usuario de la base de datos
			Ej: "dspace"
BD_PASSWORD:		Contraseña del usuario de la base de datos
			Ej: "password"	
URL_BASE:		Dirección y puerto de la instalación de DSpace
			Ej: "http://200.66.82.41:8080"

Ejemplo de ejecución de DSpaceLoader+TopicModeling:
	sudo ./DSpaceLoader+TopicModeling.sh

*******ES NECESARIO CORRER EL SCRIPT CON PERMISOS DE SUPER USUARIO (SUDO)******

