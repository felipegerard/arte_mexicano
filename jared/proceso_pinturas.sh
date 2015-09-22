
##Identifico todas los archivos jpg y los guardo en un archivo.
echo "Encontrando los JPG´s"
find Libros -name '*.jpg'>todos_jpg.txt

##Los mando a identificar si tienen imagenes en el archivo en python y crea
##un listado con todos los que identifico con pinturas
echo "Identificando las paginas con pinturas"
python identificar_pinturas.py

##Hago un directorio en donde voy a mandar a guardar todas los archivos con
##imagenes
echo "Creando directorio"
rm -r pinturas; mkdir pinturas

##Finalmente copio todos los archivo identificados al directorio pinturas
echo "Copiando las imagenes al nuevo directorio"
cat imagenes.csv | xargs cp -t pinturas

##Creo una copia esos JPG´s a un nuevo directorio para reducirles el tamaño
echo "Copiando a nueva carpeta"
rm -r pinturas/jpgs_reducidos; mkdir pinturas/jpgs_reducidos
cat imagenes.csv | xargs cp -t pinturas/jpgs_reducidos

##Reduzco la imágen de estos jpgs
echo "Reduciendo a 200x300 jpgs"
mogrify -resize 200x300! pinturas/jpgs_reducidos/*.jpg

