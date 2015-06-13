#! /bin/bash

I=1

find $1 | grep '.txt' \
| while read f;
    do
    	< $f tr '\n' '|' | sed 's/|/ <br> /g' \
	| sed -E -e 's/ +/ /g' \
	| while read line;
	do
	    echo $I '|||' $f '|||' $line
	done
	((I++))
    done
