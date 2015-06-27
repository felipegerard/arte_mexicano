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
	--mac)
	SED_FLAG="-E"
	SYSTEM="Mac OSX"
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
	echo "    ./mass_pdftotext [options] -f <directory with book directories>"
	echo "Options:"
	echo "    [--mac] Use -E flag instead of -r flag for sed regexp. Used for compatibility with OSX."
	echo "    [-j|--ncores] <number of cores to be used by parallel>. Default: 4"
	echo "    [-v|--verbose] Print details about progress."
	echo "    [-h|--help]"
	echo "    [-p|--parallel_args] \"<other arguments to pass on to parallel>\""
	echo "    [-d|--pdftotext_args] \"<arguments to pass on to pdftotext>\". Default: \"-q -layout\""
	echo "Details:"
	echo "    The script searches the directory passed on with the -f flag for directories named pdf or PDF."
	echo "    It then extracts the text out of each .pdf within the directory and creates a .txt file."
	echo "    Finally, it creates a directory named txt at the same level as the pdf directory and puts all the .txt files within."
elif [[ ! "$ORIGIN" ]]
    then
	echo "Falta carpeta de origen (-f <carpeta>)..."
else
    if [[ "$CORES" ]]
	then
	    COR="--ncores $CORES"
    fi
    if [[ ! "$SED_FLAG" ]]
	then
	    SED_FLAG="-r"
	    SYSTEM="Linux"
    fi
    if [[ "$PARALLEL" ]]
	then
	    PARALLEL="-p $PARALLEL"
    fi
    if [[ "$PDFTOTEXT" ]]
	then
	    PDFTOTEXT="-d $PDFTOTEXT"
    fi
    if [[ "$VERBOSE" ]]
	then
	    VERB="--verbose"
	    echo "Source directory: " $ORIGIN
	    echo "Number of cores:  " $CORES
	    echo "System:	    " $SYSTEM
	    echo "Other arguments to pass on to parallel:" $PARALLEL
    fi
    ndir=`ls $ORIGIN | wc -l | sed 's/ //g'`
    i=1
    find $ORIGIN \
	| egrep --ignore-case "/pdf$" \
	| while read d
	    do
		if [[ "$VERBOSE" ]]
		    then
			echo ======================================================
			echo "($i/$ndir)"
		fi
		echo $d | sed $SED_FLAG 's/(.+)\/(PDF|pdf)$/\1\/txt/' | xargs mkdir 
		dirs=`echo $d | sed $SED_FLAG 's/(.+)\/(PDF|pdf)$/--from \1\/\2 --to \1\/txt/'`
		echo "./parallel_pdftotext.sh $VERB $COR $PARALLEL $PDFTOTEXT $dirs" \
		    | sed $SED_FLAG 's/ +/ /g' \
		    | bash
		i=$((i+1))
	    done
fi


