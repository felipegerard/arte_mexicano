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
		-h|--head)
		HEAD="$2"
		shift;;
		*)
		shift;;
	esac
done

if [[ "$FROM" ]] && [[ "$TO" ]]
then
	ls $FROM | head -$HEAD \
	 	| while read b;
			do
				echo $b;
				cp -r $FROM/$b/pdf/ $TO/$b ;
			done
fi