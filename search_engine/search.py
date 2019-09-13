'''
----------------------------------------------
Search words from iGem previous teams and years
Team:    MADRID_UCM
Author:  Carlos Bilbao (Zildj1an)
Version: 3.0
----------------------------------------------
'''
import sys
from bs4 import BeautifulSoup
from colorama import init
init(strip=not sys.stdout.isatty())
from termcolor import cprint
from pyfiglet import figlet_format
import time,datetime, urllib2, requests,threading, os, subprocess,string

cprint(figlet_format('iGEM Search', font='starwars'),'yellow', 'on_red', attrs=['bold'])
URL_s       = ".igem.org/Special:AllPages"
URL_2s      = []
URL_2s.append(".igem.org/wiki/index.php?title=Special%3APrefixIndex&prefix=Team%3A")
# In between the letter like A,B,C...
URL_2s.append("&namespace=0")
words       = raw_input("Words to search at iGEM [Separate by commas]: ").split(',')
years       = raw_input("What years to search at? [Separate by commas]: ").split(',')
year        = str(datetime.datetime.now().year)
verbose     = 'x'
file_s      = 'x'
file_name   = 'default'
urls        = []
results     = []
threads     = []
url_letters = []

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

def search_web(url_t):

    global urls

    try:
        html = urllib2.urlopen(url_t)
        soup = BeautifulSoup(html,  "lxml")
    except:
        if verbose == "y":
            print("Error with " + url_t)
            return

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

letters = list(string.ascii_uppercase)

# If all the urls are already stored
if os.path.isfile("urls") is False:

    for elem in years:
        url_k = "https://" + elem + URL_s
        search_web(url_t=url_k)

        for letter in letters:
            search_web(url_t = "https://" + str(elem) + URL_2s[0] + letter + URL_2s[1])

        file_close = open("urls","w")

        for link in urls:
            file_close.write(link)
            file_close.write("\n")
        file_close.close()
else:
        with open("urls", "r") as filehandle:
               for line in filehandle:
                    current = line[:-1]
                    urls.append(current)

# [4] Now that we have all the links, we retrieve and match text

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0',
    'X-Requested-With': 'XMLHttpRequest',
}

print("The following webs contain some of the given words:")
print("###################################################")
time.sleep(1)

if file_s == "y":
   file0 = open(file_name + "0", "w")
   file1 = open(file_name + "1", "w")
   file2 = open(file_name + "2", "w")
   file3 = open(file_name + "3", "w")

size = len(urls) / 4
url_chunk = []

# [5] Divide work weight in three threads

for i in range(0, len(urls), size):
    url_chunk.append(urls[i:i + size])

# [6] Search independently
def search(the_urls,filen,yearsn):

        global verbose,words,results

        for link in the_urls:

                year = False

                for elem in yearsn:
                      if elem in link:
                           year = True

                if year == False:
                     return

                try:
                    response = requests.get(link, headers=headers, timeout=1.5, allow_redirects=False)
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
                                if filen == "0":
                                    file0.write(link)
                                    file0.write("\n")
                                elif filen == "1":
                                    file1.write(link)
                                    file1.write("\n")
                                elif filen == "2":
                                    file2.write(link)
                                    file2.write("\n")
                                else:
                                    file3.write(link)
                                    file3.write("\n")
                                print(str(len(results)) + " - " + link)

thread1 = threading.Thread(target = search, args=(url_chunk[0], "0",years))
thread2 = threading.Thread(target = search, args=(url_chunk[1], "1",years))
thread3 = threading.Thread(target = search, args=(url_chunk[2], "2",years))
thread4 = threading.Thread(target = search, args=(url_chunk[3], "3",years))
threads.extend((thread1,thread2,thread3,thread4))  			# Append multiple

for t in threads:
     t.start()

# [7] Join the three files

for t in threads:
    t.join()

if file_s == "y":
    file0.close()
    file1.close()
    file2.close()
    file3.close()
    os.system("cat " + file_name + "* > " + file_name)
    os.system("rm " + file_name + "0")
    os.system("rm " + file_name + "1")
    os.system("rm " + file_name + "2")
    os.system("rm " + file_name + "3")

print("Number of webs with match : " + str(len(results)))
