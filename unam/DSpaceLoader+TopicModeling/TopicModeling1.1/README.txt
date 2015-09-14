TopicModelingV1.1
31/08/2015
Sistema desarrollado por el GIL, Instituto de Ingeniería UNAM
Contacto:
	Carlos González Gallardo
	cgonzalezg@iingen.unam.mx

+---INFORMACIÓN---+
*TopicModelingV1.1 está diseñado para correr en sistemas Unix o similares, ha sido probado en distribuciones Linux (Ubuntu y OpenSuse) así como en Apple OS X Yosemite.
*TopicMOdeling V1.1 extrae el texto de los archivos pdf que se encuentran en la carpeta indicada, una vez extraido el texto obtiene el idioma deduce el idioma del libro almacenándolo en la carpeta de idioma correspondiente. Por cada carpeta de idioma generada realiza una comparación semántica de los libros obteniendo un diccionario de similitudes. Finalmente escribe un archivo xml con el formato requerido por DSpace en donde muestra aquellos libros con una distancia coseno >= 0.5.

+---REQUISITOS MÍNIMOS DEL SISTEMA---+
Topic Modeling V1.1  está compuesto por un conjunto de scripts de Python; por lo que el intérprete de pyton 2.7 debe estar instalado en el sistema.
El uso del procesador y memoria RAM así como de Disco Duro depende totalmente de la cantidad de libros a procesar.

+---DEPENDENCIAS---+
TopicModelingV1.1 hace uso de bibliotecas externas que son código abierto. Al iniciarse TopicModelingV1.1 se  hace una revisión de las bibliotecas necesarias, en caso de faltar alguna cancela toda acción posterior.
Paquetes necesarios para el correcto funcionamiento de TopicModelingV1.1:
	pdfminer
	gensim
	nltk

Es recomendable tener instalado "easy_install" para hacer la instalación de estos paquetes. "easy_install" se encuentra en "setuptools 18.0.1", las instrucciones de descarga e instalación se pueden consultar en la siguiente liga: https://pypi.python.org/pypi/setuptools
Instalación de "setuptools" en sistemas UNIX: "wget https://bootstrap.pypa.io/ez_setup.py -O - | python" 
Una vez instalado "easy_install", la instalación de los paquetes es muy sencilla:
	sudo easy_install [nombre del paquete]
	Ejemplo: sudo easy_install pdfminer

+---EJECUCIÓN---+
La ejecución de TopicModelingV1.1 se hace mediante el wrapper llamado "TopicModeling.sh", éste es necesario que cuente con permisos de ejecución. SI SE INTENTA EJECUTAR TopicModelingV1.1 DIRECTAMENTE EN ALGUNO DE LOS SCRIPTS LOCALIZADOS EN LA CARPETA "scripts" ES POSIBLE QUE SE PRESENTE ALGÚN COMPORTAMIENTO IRREGULAR.
Al momento de ejecutar TopicModelingV1.1 es necesario especificarle 7 parámetros que son obligatorios, si se omite alguno de ello o se ingresa algún otro, TopicModelingV1.1 mostrará un mensaje de error.


-PARÁMETROS-
Los 7 parámetros descrito a continuación son OBLIGATORIOS para DSpaceLoader V2 y deben ser indicados en el orden establecido.
	1.- [ruta_general]
		Carpeta en donde se localizan los libros
		Ej: "/export/dspacearchive/libros"
	2.- [ruta_base_txts]
		Carpeta en donde se colocarán los libros en txt
		Ej: "/export/dspacearchive/txt"
	3.- [ruta_lsi]
		Carpeta en donde se almacenarán las estructuras de LSI
		Ej: "/export/dspacearchive/lsi"
	4.- [ruta_xml]
		Carpeta en donde se colocará el archivo xml
		Ej: "/home/dspaceadmin/dspace/webapps/xmlui/themes/Mirage/lib/xsl/aspect/artifactbrowser"
	5.- [bd_usuario]
		Usuario de la base de datos
		Ej: "dspace"
	6.- [bd_password]
		Contraseña del usuario de la base de datos
		Ej: "password"
	7.- [url_base]
		Dirección y puerto de la instalación de DSpace
		Ej: "http://200.66.82.41:8080"

Ejemplo de ejecución de TopicModelingV1.1:
	./TopicModeling.sh  /export/dspacearchive/libros /export/dspacearchive/txt /export/dspacearchive/lsi/ /home/dspaceadmin/dspace/webapps/xmlui/themes/Mirage/lib/xsl/aspect/artifactbrowser dspace  password  http://200.66.82.41:8080

