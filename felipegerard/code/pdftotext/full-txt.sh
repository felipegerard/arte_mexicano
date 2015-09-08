#! /bin/bash


while [[ $# > 0 ]]
    do
	key="$1"

	case $key in
	    -f|--directory)
	    ORIGIN="$2"
	    shift
	    ;;
	    *) 
	    shift
	    ;;
	esac
    done


if  [ ! "$ORIGIN" ]
    then
    echo "Falta carpeta de origen (-f <carpeta>)..."
else
    ndir=`ls $ORIGIN | wc -l | sed 's/ //g'`
    #i=1
    find $ORIGIN \
	 | egrep --ignore-case "/txt$" \
	 | while read d
	     do
		 dirs=`echo $d | gsed -r 's/(.+)\/(txt)$/ \1/'`
		 mkdir $d/full/
		 cat $d/*.txt > $d/full/${dirs##*/}.txt
		 echo $d/full/${dirs##*/}.txt
	     done
fi
