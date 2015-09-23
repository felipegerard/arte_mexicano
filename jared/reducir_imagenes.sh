#!/bin/bash

##Reduzco la imágen de estos jpgs
echo "Reduciendo a 200x300 jpgs"
mogrify -resize 200x300! $1/*.jpg
