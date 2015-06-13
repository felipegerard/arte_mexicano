#! /bin/bash
# AUTHOR: Felipe Gerard V.
# DETAILS: Wraps parallel and pdftotext in a convenient way.
#	   The user must provide a directory with PDF files and a target directory to put the converted .txt files
# REQUIREMENTS: parallel and pdftotext must be in a directory in the PATH variable

while [[ $# > 0 ]]
do
    key="$1"

    case $key in
	-f|--from)
	FROM="$2"
	shift
	;;
	-t|--to)
	TO="$2"
	shift
	;;
	-j|--ncores)
	CORES="$2"
	shift
	;;
	-v|--verbose)
	VERBOSE=true
	shift
	;;
	-h|--help)
	HELP=true
	shift
	;;
	-p|--parallel_args)
	PARALLEL="$2"
	shift
	;;
	-d|--pdftotext_args)
	PDFTOTEXT="$2"
	shift
	;;
	*) # unknown option
	;;
    esac
    shift
done

if [ $HELP ]
    then
	echo "Uso:"
	echo "    ./parallel_pdftotext -f <carpeta con PDFs> -t <carpeta destino TXT>"
	echo "Opciones:"
	echo "    [-j|--ncores] <numero de cores para parallel>. Default: 4"
	echo "    [-v|--verbose]"
	echo "    [-h|--help]"
	echo "    [-p|--parallel_args] \"<otros argumentos a pasar a parallel>\""
	echo "    [-d|--pdftotext_args] \"<argumentos a pasar a parallel>\". Default: \"-q -layout\""
elif [[ ! "$FROM" ]]
    then
	echo "Falta carpeta de origen (-f <carpeta>)..."
elif [[ ! "$TO" ]]
    then
	echo "Falta carpeta de destino (-t <carpeta>)..."
else
    if [[ ! "$CORES" ]]
	then
	    CORES=4
    fi
    if [[ ! "$VERBOSE" ]]
	then
	    VERBOSE=false
    fi
    if [[ ! "$PDFTOTEXT" ]]
	then
	    PDFTOTEXT="-layout -q"
    fi
    if [ $VERBOSE ]
	then
	    echo "Carpeta de origen:  " $FROM
	    echo "Carpeta de destino: " $TO
	    echo "Numero de nucleos:  " $CORES
	    echo "Otros args parallel:" $PARALLEL
    fi
    find $FROM | egrep '\.pdf$|.PDF$' \
	| parallel $PARALLEL -j $CORES "pdftotext $PDFTOTEXT {} $TO/{/.}.txt"
fi















