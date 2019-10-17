'''
----------------------------------------------
Search words from iGem previous teams and years
Team:    MADRID_UCM
Author:  Carlos Bilbao (Zildj1an)
Version: 4.0 (GUI)
----------------------------------------------
'''
import sys
from bs4 import BeautifulSoup
from colorama import init
init(strip=not sys.stdout.isatty())
from termcolor import cprint
from pyfiglet import figlet_format
import time,datetime, urllib2, requests,threading, os, subprocess,string
import Tkinter
from Tkinter import *
import tkMessageBox

cprint(figlet_format('iGEM Search', font='starwars'),'yellow', 'on_red', attrs=['bold'])


 ######################################################
 # Main code (Can be modified for on-terminal work)   #
 ######################################################

def main_exe(words,years,file_name):

    URL_s       = ".igem.org/Special:AllPages"
    URL_2s      = []
    URL_2s.append(".igem.org/wiki/index.php?title=Special%3APrefixIndex&prefix=Team%3A")
    # In between the letter like A,B,C...
    URL_2s.append("&namespace=0")
    #words       = raw_input("Words to search at iGEM [Separate by commas]: ").split(',')
    #years       = raw_input("What years to search at? [Separate by commas]: ").split(',')
    year        = str(datetime.datetime.now().year)
    verbose     = 'n' # Change for on-terminal work
    file_s      = 'y'
    #file_name   = 'default'
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
    if os.path.isfile("urls_to_" + year) is False:

        for elem in years:
            url_k = "https://" + elem + URL_s
            search_web(url_t=url_k)

        for letter in letters:
            search_web(url_t = "https://" + str(elem) + URL_2s[0] + letter + URL_2s[1])

        file_close = open("urls_to_"+year,"w")

        for link in urls:
            file_close.write(link)
            file_close.write("\n")
        file_close.close()
    else:
        with open("urls_to_"+year, "r") as filehandle:
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
    def search(the_urls,filen,yearsn, words_n,verbose_n,results_n):

        for link in the_urls:

                year = False

                for elem in yearsn:
                      if elem in link:
                           year = True

                if year == False:
                     continue

                try:
                    response = requests.get(link, headers=headers, timeout=1.5, allow_redirects=False)
                except requests.exceptions.RequestException as e:
                     if verbose_n == "y":
                         print(e)
                         print("Connection error with link " + link)
                     continue

                soup = BeautifulSoup(response.text, "html.parser")

                for line in soup.find_all(text = True):

                    for word in words_n:
                        if word in line and link not in results_n:
                            results_n.append(link)
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
                                print(str(len(results_n)) + " - " + link)

    thread1 = threading.Thread(target = search, args=(url_chunk[0], "0",years,words,verbose,results))
    thread2 = threading.Thread(target = search, args=(url_chunk[1], "1",years,words,verbose,results))
    thread3 = threading.Thread(target = search, args=(url_chunk[2], "2",years,words,verbose,results))
    thread4 = threading.Thread(target = search, args=(url_chunk[3], "3",years,words,verbose,results))
    threads.extend((thread1,thread2,thread3,thread4))              # Append multiple

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


 ###################
 #  GUI            #
 ###################

top = Tkinter.Tk()
top.title("iGEM Search Engine")
frame = Frame(top)
frame.pack()
L0 = Label(frame, text = " Welcome to the iGem Search Engine open-source tool. \n Separate years and words by commas. \n Author Carlos Bilbao, 2019. \n")
L0.pack()
top_frame    = Frame(top)
bottom_frame = Frame(top)
top_frame.pack(side = TOP)
bottom_frame.pack(side = BOTTOM)
# Top top Frame
topframe = Frame(top_frame)
topframe.pack(side = TOP)
L1 = Label(topframe, text="Words to search")
L1.pack(side = LEFT)
E1 = Entry(topframe, bd=3)
E1.pack(side = RIGHT)
# Top bottom Frame
midframe = Frame(top_frame)
midframe.pack(side = BOTTOM)
L2 = Label(midframe, text = "	Years")
L2.pack(side = LEFT)
E2 = Entry(midframe, bd =3)
E2.pack(side = RIGHT)
# Bottom Top Frame
bottomframe = Frame(bottom_frame)
bottomframe.pack(side = TOP)
L3 = Label(bottomframe, text = "          File Name")
L3.pack(side = LEFT)
E3 = Entry(bottomframe, bd = 3)
E3.pack(side = RIGHT)
# Bottom bottom Frame
bbottomframe = Frame(bottom_frame)
bbottomframe.pack(side = BOTTOM)

def searchCallBack(words,years,file_name):

    main_exe(words,years,file_name)
    msg = "Search finished. You may now close these windows.\nYou can contribute to the source code at github.com/Zildj1an"
    tkMessageBox.showinfo("Search finished",msg)

B = Tkinter.Button(bbottomframe,text= "Search", command = lambda: searchCallBack(words=E1.get().split(','),years=E2.get().split(','),file_name=E3.get()), bd= 3)
B.pack(side = BOTTOM)
top.mainloop()
sys.exit()
