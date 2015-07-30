
# Problemas con S3 --> txt
aws s3 ls einformativa/biblioteca_arte/ > temp
cat temp | sed -E 's/ +PRE (.+)\/$/\1/' > lista_s3.txt
ls > lista_local.txt
grep -v -f lista_local.txt lista_s3.txt
grep -v -f lista_local.txt lista_s3.txt | while read d; do aws s3 ls einformativa/biblioteca_arte/$d/; done


# Problemas con scp de EC2 a localhost



