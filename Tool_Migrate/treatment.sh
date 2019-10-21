#!/bin/bash

# Workflow:
#
# 1. Mirror
# 2. Cleanup y renombrar archivos
# 3. Subir archivos
# 4. Transformar objetivo
# 4.1. Pasar todas las urls a relativas
# 4.2. Transformar templates
# 4.3. Transformar archivos
# 4.4. Externalizar scripts y prettificar
# 5. Transformar archivos
# 6. Subir archivos modificados y scripts
# 7. Subir objetivo


if test ! -z $5
then
	page_name=$5
else
	page_name=$1
fi

# 1. Mirror
if test ! -z $1
then
	if test $2 != '-nm'
	then
		echo Mirroring $page_name
		ssh -i Wordpress.pem bitnami@ec2-18-189-27-90.us-east-2.compute.amazonaws.com ./mirror.sh "$page_name"
		scp -r -i Wordpress.pem bitnami@ec2-18-189-27-90.us-east-2.compute.amazonaws.com:~/copy.zip .
	fi
	html_name=$1.html
else
	html_name='index.html'
fi

rm -r wcpy
unzip copy.zip > /dev/null
mv 18.189.27.90 wcpy
mv wcpy/$page_name.html wcpy/$1.html

echo Converting $name
cd wcpy

# Paso previo, convertir enlaces navegación
sed -i "s/href=[^#\s]*\.html\(#[0-9]*\)/href=\"\1/g" "$html_name"
sed -i "s/href=[^#\s]*\.html\(#nav[0-9]*\)/href=\"\1/g" "$html_name"

if test "$3" == '-t'
then
	firefox $html_name
	exit
fi

# 2. Cleanup y renombrar archivos

# remove ?
for f in $(find . -type f | grep '?')
do                                               
	mv $f $(echo $f | grep -o '^[^?]*')                   
done

# append .txt where necessary

for f in $(find wp-content wp-includes -type f | grep '\(\.js$\)\|\(\.css$\)\|\(\.orig$\)')
do
mv $f $(echo $f | sed 's/\./\~/g').txt
done

# remove woff2
for f in $(find wp-content wp-includes -type f | grep '\.woff2$')
do
rm $f
done

# remove index
if test ! $name = 'index.html'
then
rm index.html*
fi

rm *.orig
find wp-content -maxdepth 1 -type f -delete
find wp-includes -maxdepth 1 -type f -delete


# 3. Subir archivos
if test "$4" == "-nu"
then
param='-c'
else
param=""
fi

cd ..
echo "Uploading..."
./upload.py wcpy 'wp-content/**/*' -n $param
cp links.txt links.txt.old1
cat new_links.txt >> links.txt
./upload.py wcpy 'wp-includes/**/*' -n $param
cp links.txt links.txt.old2
cat new_links.txt >> links.txt
cd wcpy

# Crear archivo de enlaces

if test  -f ../enlaces.txt
then
	cp ../enlaces.txt .
else
	echo "Gathering links"
	for f in $(find wp-content wp-includes -type f | grep -v '\(\.js\)\|\(\.css\)\|\(\.html\)')
	do
		name=$(echo $f | sed 's/\//\~/g')
        wget "https://2019.igem.org/File:T--MADRID_UCM--$name" -o /dev/null -O data
        data=$(cat data)
        echo $data | grep -o '/wiki/images/[^ "]*' | grep 'T' | grep -v '/[0-9]*px' | sort -u
    done > enlaces.txt
	sed -i 's/.*[0-9]*px.*//g' enlaces.txt
	sed -i 's/^\n//g' enlaces.txt
	sort -u enlaces.txt > enl2
	mv enl2 enlaces.txt
	cp enlaces.txt ../enlaces.txt
fi


# 4. Transformar objetivo

# 4.1. Pasar todas las urls a relativas y formato estándar
sed -i 's/http:\/\/18\.189\.27\.90\/wp-/wp-/g' $html_name

# change ~ and .txt
grep -o "wp-[^. \\]*\(\.[^\\'\<>\.,;\" ()=+*?]*\)*" $html_name | grep '\.' > subs.txt
sed 's/\//\~/g' subs.txt > subsv.txt

grep '\(\.js$\)\|\(\.css$\)\|\(\.orig$\)' subsv.txt > toconv.txt

sed 's/\./\~/g' toconv.txt | sed 's/$/.txt/' > converts.txt

# test change
while read -r a && read -r b <&3
do
if test $b != $(echo $a | sed 's/\./\~/g' | sed 's/$/.txt/' )
then
	echo Not equal
fi 
done < toconv.txt 3<converts.txt

sed -i 's/\//\\\//g' subs.txt
sed -i 's/\./\\\./g' subs.txt
sed -i 's/\~/\\\~/g' subsv.txt
sed -i 's/\./\\\./g' toconv.txt
sed -i 's/\~/\\\~/g' toconv.txt
sed -i 's/\~/\\\~/g' converts.txt

# Substitute in file
while read -r a && read -r b <&3 
do
sed -i "s/$a/$b/g" $html_name
done < subs.txt 3<subsv.txt

while read -r a && read -r b <&3 
do
sed -i "s/$a/$b/g" $html_name
done < toconv.txt 3<converts.txt


# 4.2. Transformar templates
sed -i 's/\(wp-content[^.]*\~js\.txt\)/https:\/\/2019.igem.org\/wiki\/index.php?title=Template:MADRID_UCM\/\1\&action=raw\&ctype=text\/javascript/g' $html_name
sed -i 's/\(wp-content[^.]*\~css\.txt\)/https:\/\/2019.igem.org\/wiki\/index.php?title=Template:MADRID_UCM\/\1\&action=raw\&ctype=text\/css/g' $html_name
sed -i 's/\(wp-includes[^.]*\~js\.txt\)/https:\/\/2019.igem.org\/wiki\/index.php?title=Template:MADRID_UCM\/\1\&action=raw\&ctype=text\/javascript/g' $html_name
sed -i 's/\(wp-includes[^.]*\~css\.txt\)/https:\/\/2019.igem.org\/wiki\/index.php?title=Template:MADRID_UCM\/\1\&action=raw\&ctype=text\/css/g' $html_name


# 4.3. Transformar archivos

for line in $(find wp-content wp-includes -type f | grep -v '\.txt')
do
	name=$(echo $line | grep -o '/[^/]*$' | grep -o '[^/]*')
	cline=$(grep "~$name" enlaces.txt)
	if test ! -z "$cline"
	then
		nline=$(echo $line | sed 's/\//\\\~/g' | sed 's/\./\\\./g')
		cline=$(echo $cline | sed 's/\//\\\//g' | sed 's/\./\\\./g' | sed 's/\~/\\\~/g')
		sed -i "s/$nline/$cline/g" $html_name
	else
		echo Unmatched $line
		cline=$(grep "~$name" ../links.txt)
		if test ! -z "$cline"
		then
			wget "$cline" -o /dev/null -O data
	    	data=$(cat data)
	    	echo $data | grep -o '/wiki/images/[^ "]*' | grep 'T' | grep -v '/[0-9]*px' | sort -u >> enlaces.txt
			name=$(echo $line | grep -o '/[^/]*$' | grep -o '[^/]*')
			cline=$(grep "~$name" enlaces.txt)
			nline=$(echo $line | sed 's/\//\\\~/g' | sed 's/\./\\\./g')
			cline=$(echo $cline | sed 's/\//\\\//g' | sed 's/\./\\\./g' | sed 's/\~/\\\~/g')
			sed -i "s/$nline/$cline/g" $html_name
		else
			echo $name not found
		fi
fi
done

sed -i 's/.*[0-9]*px.*//g' enlaces.txt
sed -i 's/^\n//g' enlaces.txt
sort -u enlaces.txt > enl2
mv enl2 enlaces.txt
cp enlaces.txt ../enlaces.txt


# 4.4 Externalizar scripts y prettificar
tr_name=$(echo $html_name | sed 's/\./\~/g')
mv $html_name $tr_name
mkdir html
../scriptify.py $tr_name html
mv $tr_name.new $html_name
find html -type f > uploads.txt

# 6. Subir archivos modificados y scripts

cd ..
./upload.py wcpy -f 'uploads.txt' -n -r $param
cp links.txt links.txt.old3
cat new_links.txt >> links.txt
cd wcpy

sed -i 's/.*DOCTYPE.*/{{MADRID_UCM\/html\/main}}/g' $html_name
sed -i 's/\(<body.*\)/\1\n<div class="header-sticky-both wpb-js-composer">/g' $html_name
sed -i 's/\(<\/body.*\)/<\/div>\n\1/g'	$html_name

cd ..
./upload.py wcpy $html_name -h -n $param
cp links.txt links.txt.old4
cat new_links.txt >> links.txt
