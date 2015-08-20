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
	--mac)
	SED_FLAG="-E"
	SYSTEM="Mac OSX"
	shift;;
	*)
	shift;;
    esac
done

function txt2psv() {
    # args: file output
    < $1 tr '[:upper:]' '[:lower:]' \
	| sed -E -e 's/[^0-9a-záéíóúüñ ]/ /g' -e 's/ +/ /g' \
	| tr ' ' '\n' \
	| grep -E '.' \
	| sort \
	| uniq -c \
	| sed -E 's/ *([^ ]+) ([^ ]+)/\1|\2/' \
	> $2
}
export -f txt2psv

if [[ ! "$SED_FLAG" ]]
then
    SED_FLAG="-r"
    SYSTEM="Linux"
fi

if [ -d "${FROM}" ]
then
    echo DIR
    find $FROM \
	| sed 1d \
	| parallel $PARALLEL txt2psv {} $TO/{/.}.psv
else
    echo FILE
    txt2psv "${FROM}" "${TO}"
fi





