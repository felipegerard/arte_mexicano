
BUCKET=einformativa/biblioteca_arte/
SED_FLAG='-r'
dir_list=`aws s3 ls --recursive $BUCKET \
	 | head -1000 \
	 | sed $SED_FLAG 's/ +/|/g' \
	 | cut -d'|' -f4 \
	 | sed $SED_FLAG 's/(.*)\/([^/]+\/[^/]+\/)([^/]+)$/\2/' \
	 | grep --ignore-case 'pdf/$' \
	 | uniq`
