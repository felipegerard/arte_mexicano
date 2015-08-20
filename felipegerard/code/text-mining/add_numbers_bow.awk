BEGIN {
    i=0
	prev=""
	FS="|"
	OFS="|"
}
{
    if($1!=prev){
	i++
	    prev=$1
    }
    print i, $1, $2, $3 
}
