#! /bin/bash


while [[ $# > 0 ]]
do
    key="$1"

    case $key in
	-f|--directory)
	ORIGIN="$2"
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

echo "JAJAAJ" 
find $ORIGIN | egrep --ignore-case "/PDF$|pdf$"



