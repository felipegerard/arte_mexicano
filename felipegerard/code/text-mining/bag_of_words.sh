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
	*)
	shift;;
    esac
done

txt2psv(){
    # args: file output
    < $1 tr '[:upper:]' '[:lower:]' \
	| sed -E -e 's/[^0-9a-záéíóúüñ ]/ /g' -e 's/ +/ /g' \
	| tr ' ' '\n' \
	| grep -E '.' \
	| sort \
	| uniq -c \
	| sed -E 's/ +([^ ]+) ([^ ]+)/\1|\2/' \
	> $2
}

#txt2psv $FROM $TO

if [ -d "${FROM}" ]
then
    echo DIR
else
    echo FILE
    txt2psv "${FROM}" "${TO}"
fi
