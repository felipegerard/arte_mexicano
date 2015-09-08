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
	shift
	;;
    esac
done

if [ $HELP ]
    then
	echo "Usage:"
	echo "    ./parallel_pdftotext [options] -f <directory with PDFs> -t <target directory for TXT files>"
	echo "Options:"
	echo "    [-j|--ncores] <number of cores to be used by parallel>. Default: 4"
	echo "    [-v|--verbose]"
	echo "    [-h|--help]"
	echo "    [-p|--parallel_args] \"<other arguments to pass on to parallel>\""
	echo "    [-d|--pdftotext_args] \"<arguments to pass on to pdftotext>\". Default: \"-q -layout\""
elif ! type pdftotext >/dev/null
    then
	echo "ERROR: pdftotext not found. Install it and make sure it is on your PATH."
	echo "    Mac: brew instal xpdf *or* brew install poppler."
	echo "    Linux: sudo apt-get install poppler-utils"
elif ! type parallel >/dev/null
    then
	echo "ERROR: parallel not found. Install it and make sure it is on your PATH"
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
    if [[ ! "$PDFTOTEXT" ]]
	then
	    PDFTOTEXT="-layout -q"
    fi
    if [[ "$VERBOSE" ]]
	then
	    echo "Source directory:  " $FROM
	    echo "Target directory: " $TO
	    echo "Number of cores:  " $CORES
	    echo "Other arguments to pass on to parallel:" $PARALLEL
    fi
    find $FROM | egrep '\.pdf$|.PDF$' \
	| parallel $PARALLEL -j $CORES "pdftotext $PDFTOTEXT {} $TO/{/.}.txt"
fi















