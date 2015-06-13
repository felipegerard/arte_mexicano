#! /bin/bash

curl -s http://op.efinf.com/arteMX/ | pup 'a' | grep -v '<' | grep '/' \
| while read d;
do
    #echo $d
    mkdir $d
    cd $d
    curl -s http://op.efinf.com/arteMX/$d | pup 'a' | grep -v '<' | grep '/' \
    | while read dd;
    do
	#echo http://op.efinf.com/arteMX/$d$dd
	mkdir $dd
	cd $dd
	curl -s http://op.efinf.com/arteMX/$d$dd | pup 'a' | grep -v '<' | grep '[0-9]' | sed 's/ //g' \
	| parallel --progress -j50 "echo http://op.efinf.com/arteMX/$d$dd{} | xargs curl -s > {}"
	cd ..
    done
    cd ..
done
