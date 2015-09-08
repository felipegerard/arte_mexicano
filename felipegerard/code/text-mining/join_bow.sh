#! /bin/bash

while [[ $# > 0 ]]
do
    key="$1"
    case $key in
	-f|--from)
	FROM="$2"
	shift;;
	-t|--to)
	TO="$2"
	shift;;
	-p|--parallel_args)
	PARALLEL="$2"
	shift;;
	--force)
	FORCE=true
	shift;;
	-n|--dry-run)
	DRYRUN=true
	shift;;
	*)
	shift;;
    esac
done

if [ -z "$FROM" ] || [ -z "$TO" ]
then
    echo 'ERROR: Please provide a source directory and a target file.'
else
    if [ -f $TO ] && [ ! $FORCE ]
    then
	echo "ERROR: The file '$TO' already exists. Use option [--force] to override."
    else
	echo "Source directory: $FROM"
	echo "Target file:      $TO"
	if [ ! "$DRYRUN" ]
	then
	    find $FROM \
		| sed 1d \
		| parallel --keep-order $PARALLEL "< {} awk -F'|' 'BEGIN {OFS=\"|\"}{print \"{/.}\", \$2, \$1}'" \
		| awk -f add_numbers_bow.awk \
	    > $TO
	fi
    fi
fi
