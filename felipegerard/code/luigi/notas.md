
## Detección de idioma
Instalar los modulos que hacen falta

$ pip install nltk
import nltk
nltk.download('stopwords')

## 
$ pip install pdfminer
$ pip install markdown

$ pip install networkx
$ pip install GraphViz
$ brew install graphviz
$ pip install pydot

## Estructura de archivos de entrada
+ ruta_fuente_pdfs (podría ser ruta_general/pdf, aunque no tiene que ser)
+ ruta_general/txt/
    * librosAgregados.tm
    * idiomas.tm
    * spanish
    * english
    * ...

## To do
++ Por qué no funciona TrainLDA cuando workers > 1?
++ Usar una sola carpeta y filtrar con metadatos??
+ Quitar los parámetros sobrantes (meta...)
+ Guardar txts crudos? Por página?
+ LSA (requiere stopwords?)
+ XMLs DSpace

## Trabajo futuro
+ Paralelizar por idioma (checar que alcance la memoria)
+ Mejorar el uso de Gensim, por ejemplo para actualizar en lugar de reescribir, etc.

## OJO
+ Toman las primeras 6 letras de las palabras como tipo stemming simple.
