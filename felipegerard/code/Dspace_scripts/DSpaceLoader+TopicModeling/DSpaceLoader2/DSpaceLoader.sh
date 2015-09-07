#!/bin/bash
#DSpaceLoader V2
#########
#	31/08/2015
#	Sistema desarrollado por el GIL, Instituto de Ingenieria UNAM
#	cgonzalezg@iingen.unam.mx
#########

#NOTA: La entrada al sistema debe ser única y exclusivamente a través de este script
cd "$(dirname "$0")"
python ./scripts/DSpaceLoader.py $1 $2 $3 $4 $5
