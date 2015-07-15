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
	echo "    ./s3_pdftotext [options] -b <S3 bucket> -t <target local directory>"
	echo "Options:"
	echo "    [--mac] Use -E flag instead of -r flag for sed regexp. Used for compatibility with OSX."
	echo "    [-j|--ncores] <number of cores to be used by parallel>. Default: 4"
	echo "    [-v|--verbose] Print details about progress."
	echo "    [-h|--help]"
	echo "    [-p|--parallel_args] \"<other arguments to pass on to parallel>\""
	echo "    [-d|--pdftotext_args] \"<arguments to pass on to pdftotext>\". Default: \"-q -layout\""
	echo "Details:"
	echo "    The script searches the S3 bucket passed on with the -b flag for directories named pdf or PDF."
	echo "    It then extracts downloads a copy of each folder and converts it to TXT on a folder at the same level as the copy of the PDF folder."
	echo "    Finally, it removes the PDF folder to save space."
	echo "    NOTICE: This script does NOT upload any information to S3."
	echo "    WARNING: Provide an empty local directory to avoid collision and possible loss of information."
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
	    echo "Target directory: " $TO
	    echo "Number of cores:  " $CORES
	    echo "System:	    " $SYSTEM
	    echo "Other arguments to pass on to parallel:" $PARALLEL
    fi
    ndir=`aws s3 ls --recursive $BUCKET | grep --ignore-case 'pdf/$' | wc -l`
    i=1
    aws s3 ls --recursive $BUCKET \
	| grep --ignore-case 'pdf/$' \
	| sed $SED_FLAG 's/.+ +[0-9]+ //' \
	| while read d;
	    do
		if [[ "$VERBOSE" ]]
		    then
			echo ==================================================================
			echo "($i / $ndir): $d | sed $SED_FLAG 's/(.+)\/(PDF|pdf)\/$/\1/'"
		fi
		dfix=`echo $d | sed $SED_FLAG 's/ +/_/g'`
		txt=`echo $d | sed $SED_FLAG 's/(.+)\/(PDF|pdf)\/$/\1\/txt\//'`
		aws s3 cp --recursive --quiet s3://$BUCKET/$d $TO/$d
		mkdir $TO/$txt
		./parallel_pdftotext.sh $VERB $COR $PARALLEL $PDFTOTEXT --from $TO/$d --to $TO/$txt
		rm -r $TO/$d
		i=$((i+1))
	    done


fi




