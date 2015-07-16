#! /bin/bash


while [[ $# > 0 ]]
do
    key="$1"

    case $key in
	-f|--from)
	ORIGIN="$2"
	shift
	;;
	-b|--bucket)
	BUCKET="$2"
	shift
	;;
	-d|--delete-files)
	DELETE=true
	shift
	;;
	-j|--ncores)
	CORES="$2"
	shift
	;;
	-v|--verbose)
	VERBOSE=true
	QUIET=''
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
	*) # unknown option
	shift
	;;
    esac
done


if [ $HELP ]
    then
	echo "Usage:"
	echo "    ./s3_upload_txt.sh [options] -f <local directory with txt folders> -b <S3 bucket to upload to>"
	echo "Options:"
	echo "    [--mac] (not used) Use -E flag instead of -r flag for sed regexp. Used for compatibility with OSX."
	echo "    [-j|--ncores] <number of cores to be used by parallel>. Default: 4"
	echo "    [-v|--verbose] Print details about progress."
	echo "    [-h|--help]"
	echo "    [-p|--parallel_args] \"<other arguments to pass on to parallel>\""
	echo "Details:"
	echo "    This script uploads all txt directories generated with s3_pdftotext.sh to their corresponding location"
	echo "    in the given S3 bucket."
	echo "NOTE: This script uses parallel for uploading, so use the option '-p \"--progress\"' or '-p \"--eta\"' for more information on progress"

elif [[ ! "$BUCKET" ]]
    then
	echo "Please supply an AWS S3 bucket (-b s3://<bucket>)..."
elif [[ ! "$ORIGIN" ]]
    then
	echo "Please supply an empty local directory (-t <local directory>)..."
else
    if [[ "$CORES" ]]
	then
	    COR="-j $CORES"
    fi
    if [[ ! "$SED_FLAG" ]]
	then
	    SED_FLAG="-r"
	    SYSTEM="Linux"
    fi
    if [[ "$VERBOSE" ]]
	then
	    VERB="--verbose"
	    echo "Source directory: " $ORIGIN
	    echo "Target S3 bucket: " $BUCKET
	    echo "Number of cores:  " $CORES
	    echo "System:	    " $SYSTEM
	    echo "Other arguments to pass on to parallel:" $PARALLEL
    else
	QUIET='--quiet'
    fi
    find $ORIGIN \
	| grep '/txt$' \
	| cut -d'/' -f2-3 \
	| parallel $COR $PARALLEL \
	    aws s3 cp $QUIET --recursive $ORIGIN/{} s3://$BUCKET/{}
    if [ $DELETE ]
	then
	    find $ORIGIN \
		| grep '/txt$' \
		| cut -d'/' -f2-3 \
		| while read d;
		    do
			rm -r $ORIGIN/$d
		    done
    fi

fi




