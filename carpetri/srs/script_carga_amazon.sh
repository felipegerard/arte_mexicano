#!/bin/bash

echo time
head -4 ../catalogo_arte.txt

ls /media/ironman/My\ Passport/digitalizacion/ | head -8  | parallel  's3cmd -r sync /media/ironman/My\ Passport/digitalizacion/{} s3://einformativa/biblioteca_arte/'
