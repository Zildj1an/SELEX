#!/usr/bin/python3

from bs4 import BeautifulSoup
import sys

f = open(sys.argv[1])
soup = BeautifulSoup(f.read(),features="html5lib")
f.close()

i = 0
for sc in soup.findAll("script"):
	if (len(sc.contents) == 0):
		continue
	else:
		scr_name = f"{sys.argv[1]}_sc{i}~js.txt"
		scr_path = f"{sys.argv[2]}/{scr_name}"
		nf = open(scr_path, "w")
		nf.write("".join(sc.contents))	
		nf.close()
		sc.contents = []
		sc.attrs['src'] = f'/wiki/index.php?title=Template:MADRID_UCM/{sys.argv[2]}~{scr_name}&action=raw&ctype=text/javascript'
		i += 1

nf = open(sys.argv[1]+'.new', 'wb')
nf.write(soup.prettify('utf-8'))
