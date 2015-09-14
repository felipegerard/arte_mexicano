DSpaceLoader V2
31/08/2015
Sistema desarrollado por el GIL, Instituto de Ingeniería UNAM
Contacto:
	Carlos González Gallardo
	cgonzalezg@iingen.unam.mx

+---INFORMACIÓN---+
*DSpaceLoader V2 está diseñado para correr en sistemas Unix o similares, ha sido probado en distribuciones Linux (Ubuntu y OpenSuse) así como en Apple OS X Yosemite.
*DSpaceLoader V2 busca por cada libro de la dirección web indicada (o del filesystem) una carpeta llamada "pdf" de la cual extrae las hojas escaneadas y la carpeta "jpg" de la cual extrae la imagen de portada del libro por lo que es necesario respetar el formato indicado.

+---REQUISITOS MÍNIMOS DEL SISTEMA---+
DSpaceLoader V2 está compuesto por un conjunto de scripts de Python; por lo que el intérprete de pyton 2.7 debe estar instalado en el sistema.
El uso del procesador y memoria RAM así como de Disco Duro depende totalmente de la cantidad de archivos PDF a extraer del servidor.

+---DEPENDENCIAS---+
DSpaceLoader V2 hace uso de bibliotecas externas que son código abierto. Al iniciarse DSpaceLoader V2 hace una revisión de las bibliotecas necesarias, en caso de faltar alguna cancela toda acción posterior.
Paquetes necesarios para el correcto funcionamiento de DSpaceLoader V2:
	openpyxl
	pyPdf2
	pdfminer

Es recomendable tener instalado "easy_install" para hacer la instalación de estos paquetes. "easy_install" se encuentra en "setuptools 18.0.1", las instrucciones de descarga e instalación se pueden consultar en la siguiente liga: https://pypi.python.org/pypi/setuptools
Instalación de "setuptools" en sistemas UNIX: "wget https://bootstrap.pypa.io/ez_setup.py -O - | python" 
Una vez instalado "easy_install", la instalación de los paquetes es muy sencilla:
	sudo easy_install [nombre del paquete]
	Ejemplo: sudo easy_install openpyxl

+---EJECUCIÓN---+
La ejecución de DSpaceLoader V2 se hace mediante el wrapper llamado "DSpaceLoader.sh", éste es necesario que cuente con permisos de ejecución. SI SE INTENTA EJECUTAR DSpaceLoader V2 DIRECTAMENTE EN ALGUNO DE LOS SCRIPTS LOCALIZADOS EN LA CARPETA "scripts" ES POSIBLE QUE SE PRESENTE ALGÚN COMPORTAMIENTO IRREGULAR.
Al momento de ejecutar DSpaceLoader V2 es necesario especificarle 5 parámetros que son obligatorios, si se omite alguno de ello o se ingresa algún otro, DSpaceLoader V2 mostrará un mensaje de error.


-PARÁMETROS-
Los 5 parámetros descrito a continuación son OBLIGATORIOS para DSpaceLoader V2 y deben ser indicados en el orden establecido.
	1.- [cantidad_libros]
		Cantidad de libros a procesar. 0: TODOS LOS LIBROS DISPONIBLES EN EL ARCHIVO DE METADATOS
		Ej: "500"
	2.- [ruta_warehouse]
		Carpeta o dirección del warehouse
		Ej: "/export/librarian"
	3.- [nombre_xlsx]
		Archivo de metadatos
		Ej: "inventario.xlsx"
	4.- [carpeta_salida]
		Carpeta en donde se colocarán los libros
		Ej: "/export/dspace/libros"
	5.- [eperson]
		Eperson que será utilizado en DSpace
		Ej: "ejemplo@gmail.com"

Ejemplo de ejecución de DSpaceLoader V2:
	./DSpaceLoader.sh 500 /export/librarian /home/User/inventario.xlsx 0 /export/dspace/libros ejemplo@gmail.com

