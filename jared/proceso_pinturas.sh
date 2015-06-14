
##Identifico todas los archivos jpg y los guardo en un archivo.

find op.efinf.com -name '*.jpg'>todos_jpg.txt

##Los mando a identificar si tienen imagenes en el archivo en python y crea
##un listado con todos los que identifico con pinturas
python identificar_pinturas.py

##Hago un directorio en donde voy a mandar a guardar todas los archivos con
##imagenes

mkdir pinturas

##Finalmente copio todos los archivo identificados al directorio pinturas

cat imagenes.csv | xargs cp -t pinturas
