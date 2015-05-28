#!/bin/bash

date
ls /media/ironman/My\ Passport/digitalizacion/ | head -80  | parallel  's3cmd -r sync /media/ironman/My\ Passport/digitalizacion/{} s3://einformativa/biblioteca_arte/'
date
