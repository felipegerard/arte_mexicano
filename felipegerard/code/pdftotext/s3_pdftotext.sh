#! /bin/bash


while [[ $# > 0 ]]
do
    key="$1"

    case $key in
	-b|--bucket)
	BUCKET="$2"
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
elif [[ ! "$BUCKET" ]]
    then
	echo "Please supply an AWS S3 bucket (-b s3://<bucket>)..."
elif [[ ! "$TO" ]]
    then
	echo "Please supply an empty local directory (-t <local directory>)..."
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
	    echo "S3 bucket: " $BUCKET
	    echo "Target dir: " $TO
	    echo "Number of cores:  " $CORES
	    echo "System:	    " $SYSTEM
	    echo "Other arguments to pass on to parallel:" $PARALLEL
    fi
    ndir=`aws s3 ls --recursive $BUCKET | grep --ignore-case 'pdf/$'`
    i=1
    aws s3 ls --recursive $BUCKET \
	| grep --ignore-case 'pdf/$' \
	| sed $SED_FLAG 's/.+ +[0-9]+ //' \
	| while read d;
	    do
		if [[ "$VERBOSE" ]]
		    then
			echo ==================================================================
			echo ($i / $ndir): $d | sed $SED_FLAG 's/(.+)\/(PDF|pdf)\/$/\1/'
		fi
		txt=`echo $d | sed $SED_FLAG 's/(.+)\/(PDF|pdf)\/$/\1\/txt\//'`
		aws s3 cp --recursive --quiet s3://$BUCKET/$d $TO/$d
		mkdir $TO/$txt
		./parallel_pdftotext.sh $VERB $COR $PARALLEL $PDFTOTEXT --from $TO/$d --to $TO/$txt
		rm -r $TO/$d
		i=$((i+1))
	    done


fi




