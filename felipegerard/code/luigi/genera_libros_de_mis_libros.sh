
# Correr desde $HOME
ruta="Dropbox/Libros"
lista=$(ls $ruta)
mkdir "data-science/arte-mexicano/felipegerard/code/luigi/test/temp"


for i in $(ls $ruta | grep -v ' ')
do
	b=$(echo ${i} | sed 's/.pdf//' | sed 's/ /_/g')
	echo cp "$ruta/${i} data-science/arte-mexicano/felipegerard/code/luigi/test/temp/${b}/${i}"
done

echo mkdir "data-science/arte-mexicano/felipegerard/code/luigi/test/temp/${b}"

