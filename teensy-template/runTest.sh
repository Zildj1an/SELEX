#!/bin/bash
printf %b '\n' | dterm /dev/ttyACM0 crlf > /dev/null
printf %b%b%b '{"command":"runTest","test":"' $1 '"}\n' | dterm /dev/ttyACM0 crlf > tmp
sed '1d;$d' tmp > testres
while [ $(cat tmp | wc -l) -gt 5 ]
    do
        printf %b '\n' | dterm /dev/ttyACM0 crlf > tmp
        sed '1d;$d' tmp >> testres
        echo $(cat tmp | wc -l)
    done
sed 's/[^0-9\.,e-]//g' testres | grep '[0-9]' | grep '[0-9]\+,[0-9\.e-]\+,[0-9\.e-]\+' > res.csv
python plotres.py
