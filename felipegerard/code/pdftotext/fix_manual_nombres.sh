
# Problemas con S3 --> txt
aws s3 ls einformativa/biblioteca_arte/ > temp_list
cat temp_list | sed -E 's/ +PRE (.+)\/$/\1/' > lista_s3.txt
ls > lista_local.txt
grep -v -f lista_local.txt lista_s3.txt
grep -v -f lista_local.txt lista_s3.txt | while read d; do aws s3 ls einformativa/biblioteca_arte/$d/; done


# Problemas con scp de EC2 a localhost


cat lista_allfiles.txt \
    | sed -E 's/(.+biblioteca_arte\/)(.+)(\/.+)/\2/' \
    | uniq -c \
    | grep -i 'pdf' \
    | sed -E 's/^ +|\/pdf$//g' \
    | tr ' ' '|' \
    | awk -F'|' '{print $1 "|" $2}' \
    > data_frame_allfiles.psv

find . \
    | sed -E 's/(\.\/)(.+)(\/.+)/\2/' \
    | uniq -c \
    | grep -i 'txt' \
    | sed -E 's/^ +|\/txt$//g' \
    | tr ' ' '|' \
    | awk -F'|' '{print $1 "|" $2}' \
    > data_frame_local.psv
#
## jpgs y pdfs en la carpeta de pdfs
#fables_choisies_muses_en_vers_par_j._de_la_fontaif
#fables_de_la_fontaine_2
#novedades_ano_2
## pdfs corruptos? (nombre no estandar por ejemplo: prefijo_cpt_### o bien prefijo_por_### en lugar de prefijo_int_###)
#cimientos_del_artista_dibujante_y_pintor
#encuentro

## Carpetas con nombres raros
< lista_s3.txt egrep -i '[^0-9a-z_.\-]+'
