#!/bin/bash

time head -4 ../catalogo_arte.txt | parallel 's3cmd -r sync /media/ironman/My Passport/digitalizacion/{} s3://einformativa/biblioteca_arte/'