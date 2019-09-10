'''
----------------------------------------------
Search word from iGem previous teams and years
Team:    MADRID_UCM
Author:  Carlos Bilbao
Version: 2.0
----------------------------------------------
'''
import sys,time
from bs4 import BeautifulSoup
from colorama import init
init(strip=not sys.stdout.isatty())
from termcolor import cprint
from pyfiglet import figlet_format
import datetime, urllib2, requests

cprint(figlet_format('iGEM Search', font='starwars'),'yellow', 'on_red', attrs=['bold'])
URL_s     = ".igem.org/Special:AllPages"
words     = raw_input("Words to search at iGEM [Separate by commas]: ").split(',')
years     = raw_input("What years to search at? [Separate by commas]: ").split(',')
year      = str(datetime.datetime.now().year)
verbose   = 'x'
file_s    = 'x'
file_name = 'default'
urls      = []
results   = []

# [1] Delete years that are before 2008 to the current year

i = 0
for elem in years:
   if int(elem) < 2008 or elem > year:
      del years[i]
   i = i + 1

if len(years) == 0:
   print("No valid year has been given")
   sys.exit()

# [2] Verbose connection an file storing

while verbose not in ("y","n"):
     verbose = raw_input("Display connection errors? (y/n): ")

while file_s not in ("y","n"):
     file_s = raw_input("Store contents on a file? (y/n): ")
     if file_s == "y":
         file_name = raw_input("File name: ")

# [3] Search at each year

for elem in years:

    url = "https://" + elem + URL_s
    html = urllib2.urlopen(url)
    soup = BeautifulSoup(html,  "lxml")

    for link in soup.findAll('a'):
        new = link.get('href')

        if new != None:

	  # Sanitize new urls

          if elem not in new:
             new = elem + ".igem.org" + new

          if "http" not in new:

             if new[0] != "/":
                  new = "https://" + new
	     else:
                  new = "https:/" + new

          if "igem.org//" in new:
              new.replace(".org//", ".org/")

          urls.append(new)

# [4] Now that we have all the links, we retrieve and match text

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0',
    'X-Requested-With': 'XMLHttpRequest',
}

print("The following webs contain some of the given words:")
print("###################################################")
time.sleep(1)

if file_s == "y":
   file = open(file_name, "w")

for link in urls:

	try:
        	response = requests.get(link, headers=headers, timeout=0.5, allow_redirects=False)
	except requests.exceptions.RequestException as e:
	     if verbose == "y":
    		 print(e)
                 print("Connection error with link " + link)
	     continue

	soup = BeautifulSoup(response.text, "html.parser")

	for line in soup.find_all(text = True):

          for word in words:
		if word in line and link not in results:
                      results.append(link)
                      if file_s == "y":
                        file.write(link)
                        file.write("\n")
                      print(link)

if file_s == "y":
    file.close()

print("Number of webs with match : " + str(len(results)))

