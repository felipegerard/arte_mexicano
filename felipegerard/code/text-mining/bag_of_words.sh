#! /bin/bash

while [[ $# > 0 ]]
do
    key="$1"
    case $key in
	-f|--file)
	FILE="$2"
	shift;;
	-o|--output)
	OUTPUT="$2"
	shift;;
	*)
	shift;;
    esac
done

< $FILE tr '[:upper:]' '[:lower:]' \
    | sed -E -e 's/[^0-9a-záéíóúüñ ]/ /g' -e 's/ +/ /g' \
    | tr ' ' '\n' \
    | grep -E '.' \
    | sort \
    | uniq -c \
    | sed -E 's/ +([^ ]+) ([^ ]+)/\1|\2/' \
    > $OUTPUT

