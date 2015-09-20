#!/usr/bin/env bash

#Hago una seleccion aleatoria de 100 libros
aws s3 ls einformativa/biblioteca_arte/ | sort --random-sort | head -100 | awk '{ print $2 }' > libros_muestra.txt

cd Libros

#Para cada uno de los libros hago una carpeta y voy guardando la informacion
while read libro
	do
		mkdir $libro
		aws s3 cp s3://einformativa/biblioteca_arte/$libro $libro --recursive
		
done < /home/jared/CONACyT_ITAM/libros_muestra.txt
