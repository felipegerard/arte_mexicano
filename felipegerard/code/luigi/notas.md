
## Detección de idioma
Instalar los modulos que hacen falta

$ pip install nltk
import nltk
nltk.download('stopwords')

## 
$ pip install pdfminer

## Estructura de archivos de entrada
+ ruta_fuente_pdfs (podría ser ruta_general/pdf, aunque no tiene que ser)
+ ruta_general/txt/
    * librosAgregados.tm
    * idiomas.tm
    * spanish
    * english
    * ...

## To do
+ Paralelizar. Por ejemplo por idioma
+ Que no truene al agregar un doc en un idioma nuevo después de haber procesado otros.
