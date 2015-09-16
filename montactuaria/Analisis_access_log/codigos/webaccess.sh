#! /bin/bash

# webaccess - analyze an Apache-format access_log file, extracting
# useful and interesting statistics

bytes_in_gb=22048576
scriptbc="$HOME/bin/scriptbc.sh"
nicenumber="$HOME/bin/nicenumber.sh"
host="google.com"

if [ $# -eq 0 -o ! -f "$1" ] ; then
 echo "Usage: $(basename $0) logfile" >&2
 exit 1
fi

LANG=es_ES.UTF-8

#echo '<html>
#<head>
#<meta content="text/html; charset=ISO-8859-1"
#http-equiv="content-type">
#<title>'$host'</title>
#</head>
#<body>'

#echo "<pre>"

firstdate="$(head -1 "$1" | awk '{print $4}' | sed 's/\[//')"
lastdate="$(tail -1 "$1" | awk '{print $4}' | sed 's/\[//')"

echo "Results of analyzing log file $1"
echo " "
echo `uname -a`
echo "-------------------------------"
echo `date`
echo "-------------------------------"
echo " Start date: $(echo $firstdate|sed 's/:/ at /')"
echo " End date: $(echo $lastdate|sed 's/:/ at /')"

hits="$(wc -l < "$1" | sed 's/[^[:digit:]]//g')"

echo " Hits: $($nicenumber $hits) (total accesses)"

pages="$(grep -ivE '(.txt|.gif|.jpg|.png)' "$1" | wc -l | sed 's/[^[:digit:]]//g')"

echo " Pageviews: $($nicenumber $pages) (hits minus graphics)"

totalbytes="$(awk '{sum+=$10} END {print sum}' "$1")"

echo -n " Transferred: $($nicenumber $totalbytes) bytes "

if [ $totalbytes -gt $bytes_in_gb ] ; then
echo "($($scriptbc $totalbytes / $bytes_in_gb) GB)"
elif [ $totalbytes -gt 1024 ] ; then
echo "($($scriptbc $totalbytes / 1024) MB)"
else
echo ""
fi

# now let's scrape the log file for some useful data:
echo "-----------------------------------------------"
echo " "
echo "The 70 most popular pages were:"
echo "-----------------------------------------------"
echo " "
awk '{print $7}' "$1" | grep -ivE '(.gif|.jpg|.png)' | \
sed 's/\/$//g' | sort | \
uniq -c | sort -rn | head -70

echo ""
echo "The 25 most popular pages:"
echo "======================================================================"

awk '{print $7}' "$1" | grep -ivE '(mod_status|favico|crossdomain|alive.txt)' | grep -ivE '(.gif|.jpg|.png)' | \
 sed 's/\/$//g' | sort | \
 uniq -c | sort -rn | head -25

echo ""

echo " "
echo " "
echo "The 50 most common referrer URLs were:"
echo "---------------------------------------"

echo " "
echo " "
awk '{print $11}' "$1" | \
grep -vE "(^"-"$|/www.$host|/$host)" | \
sort | uniq -c | sort -rn | head -50

echo ""
#echo  "Hits by source IP:"
echo "======================================================================"

awk '{print $1}' "$1" | grep -ivE "(127.0.0.1|192.168.100.)" | sort | uniq -c | sort -rn | head -25

echo ""



#echo " "
#echo "Los 100 navegadores mas populares aqui:"
#echo "----------------------------------------"
#echo "</pre>"
#awk -F'[ "]+' '$7 == "/" { ipcount[$1]++ }
 #   END { for (i in ipcount) {
        #printf "%15s - %d\n", i, ipcount[i] } }'
#echo " "
#echo '<table style="width: 12%;" border="1" cellpadding="0" cellspacing="0"> '
#echo " "
#echo "<pre>"
#awk '{print "<tr> <td> "$12" </td> <td> "$13" </td><td> "$14" </td><td> "$15" </td><td> "$16" </td><td> "$17" </td><td> "$18" </td><td> Su IP.: <a href=\"http://network-tools.com/default.asp?prog=express&host="$1"\">"$1"</a> </td>\n"}' "$1" | \
##grep -vE "(^"-"$|/www.$host|/$host)" | \
#sort | uniq -c | sort -rn | head -100
#echo "</pre>"
#echo 
#echo '</table>
#</body>
#</html>'

exit 0