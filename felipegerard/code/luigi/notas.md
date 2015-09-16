
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
+ Filtrar páginas con imágenes
+ Guardar txts crudos? Por página?
+ LSA (requiere stopwords?)
+ Similitudes
+ XMLs DSpace
+ Paralelizar. Por ejemplo por idioma
