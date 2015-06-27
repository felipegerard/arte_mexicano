Instalación
-----------------------------------

* Instalar parallel: `sudo apt-get install parallel`
* Instalar pdftotext:
    +) Mac: `brew install xpdf` o también `brew install poppler`
    +) Linux: `apt-get install poppler-utils`
    +) De alguna otra forma, siempre y cuando esté en el PATH
* Hay que tener parallel_pdftotext.sh y mass_pdftotext.sh en la misma carpeta, con permisos para ejecutar

Uso del script
-----------------------------------

El script está en mi GitHub: https://github.com/felipegerard/arte_mexicano/tree/master/felipegerard/code/pdftotext

Conseguir ayuda:
    * Script para una carpeta:
	+) ./parallel_pdftotext --help
	+) Correr el script para un solo libro con parámetros default: `./parallel_pdftotext.sh -f <carpeta origen> -t <carpeta destino>
    * Script para transformación masiva:
	+) ./mass_pdftotext.sh --help
	+) Correr el script masivo: `./mass_pdftotext.sh -f <carpeta con todos los libros>

IMPORTANTE
-----------------------------------

Al correr el script masivo en una Mac, hay que usar la bandera `--mac` para que sed funcione correctamente.
