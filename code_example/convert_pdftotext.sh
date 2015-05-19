#! /bin/bash

find $1 | grep '.pdf' \
| parallel --progress -j8 "pdftotext -q {} txt/{/.}.txt"
