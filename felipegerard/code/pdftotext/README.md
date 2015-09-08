Instalación
-----------------------------------

* Actualizar apt-get: `sudo apt-get update`
* Instalar git: `sudo apt-get install git`
* Instalar parallel: `sudo apt-get install parallel`
* Instalar pdftotext:
    +) Mac: `brew install xpdf` o también `brew install poppler`
    +) Linux: `apt-get install poppler-utils`
    +) De alguna otra forma, siempre y cuando esté en el PATH
* Preparar S3 (sólo versión para S3):
    +) Instalar pip `sudo apt-get install python-pip`
    +) Hay que tener instalado awscli. **Debe ser la versión instalada con pip, NO con apt-get:** `sudo pip install awscli`
    +) Configurar awscli, de modo que funcione por ejemplo `aws s3 ls <bucket>`
* **IMPORTANTE:** Hay que tener todos los scripts en la misma carpeta, con permisos para ejecutar.
* **IMPORTANTE:** Hay que correr los scripts desde la carpeta donde están o bien, agregarla al PATH.
* **IMPORTANTE:** Al correr el script masivo en una Mac, hay que usar la bandera `--mac` para que sed funcione correctamente.
* Clonar el proyecto: `git clone https://github.com/felipegerard/arte_mexicano.git`
* Código fuente: https://github.com/felipegerard/arte_mexicano/tree/master/felipegerard/code/pdftotext


Ayuda
-----------------------------------

Para obtener información de cómo usar un comando, `comando --help`


Versión local
-----------------------------------

* Script para una carpeta: parallel_pdftotext.sh
    +) Correr el script para un solo libro con parámetros default: `./parallel_pdftotext.sh -f <carpeta origen> -t <carpeta destino>
* Script para transformación masiva: mass_pdftotext.sh
    +) Correr el script masivo: `./mass_pdftotext.sh -f <carpeta con todos los libros>


Versión para S3
-----------------------------------

1. Bajar PDFs carpeta por carpeta y extraer los txt (va borrando los PDFs que baja): s3_pdftotext.sh
2. Subir los txt generados por s3_pdftotext.sh a su correspondiente dirección en S3: s3_upload_txt.sh

Después de correr 1. se puede correr 2. La carpeta objetivo en 1. es la carpeta de origen en 2.
