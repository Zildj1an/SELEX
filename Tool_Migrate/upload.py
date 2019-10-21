#!/usr/bin/python3

from selenium.webdriver import Firefox
from pathlib import Path
from time import sleep
from urllib import request, error
import sys,os, threading

WEB_DIR = "."
LOG_FILE = "lastfile.log"

interactive = True
links = []
new_links_file = ""

def login(driver):
   driver.get("http://igem.org/Login2")

   user = driver.find_element_by_name("username")
   passwd = driver.find_element_by_name("password")
   login = driver.find_element_by_name("Login")

   user.send_keys("Zildj1an")
   passwd.send_keys("<passwd>")
   login.click()

def write_file(driver,textarea, fpath):

   f = (Path(WEB_DIR) / fpath).open()

   for line in f:
      driver.execute_script("arguments[0].value += arguments[1]; arguments[0].scrollTop = arguments[0].scrollHeight;",textarea,line) 


def upload_template(driver, fpath):

   driver.get(f"https://2019.igem.org/wiki/index.php?title=Template:MADRID_UCM/{str('~'.join(fpath.parts))}&action=edit")
   textarea = driver.find_element_by_id("wpTextbox1")
   textarea.clear()
   write_file(driver, textarea, fpath)
   save = driver.find_element_by_id("wpSave")
   s = input("Save?(Y/N): ") if interactive else 'Y'
   if s == 'Y':
      save.click()
      new_links_file.write(f"https://2019.igem.org/wiki/index.php?title=Template:MADRID_UCM/{str('~'.join(fpath.parts))}&action=raw\n")

def check_file_exists(fpath):

   if f"https://2019.igem.org/File:T--MADRID_UCM--{str('~'.join(fpath.parts))}" in links:
      return True
   try:
      request.urlopen(f"https://2019.igem.org/File:T--MADRID_UCM--{str('~'.join(fpath.parts))}")
   except error.HTTPError as e:
      if e.getcode() == 404:
         return False
   new_links_file.write(f"https://2019.igem.org/File:T--MADRID_UCM--{str('~'.join(fpath.parts))}\n")
   return True


def check_template_exists(fpath):

   if f"https://2019.igem.org/wiki/index.php?title=Template:MADRID_UCM/{str('~'.join(fpath.parts))}&action=raw" in links:
      return True
   try:
      request.urlopen(f"https://2019.igem.org/wiki/index.php?title=Template:MADRID_UCM/{str('~'.join(fpath.parts))}&action=raw")
   except error.HTTPError as e:
      if e.getcode() == 404:
         return False
   new_links_file.write(f"https://2019.igem.org/wiki/index.php?title=Template:MADRID_UCM/{str('~'.join(fpath.parts))}&action=raw\n")
   return True


def upload_file(driver, fpath):

   driver.get(f"https://2019.igem.org/Special:Upload")
   file_selector = driver.find_element_by_id("wpUploadFile")
   file_selector.send_keys(WEB_DIR+str(fpath))
   fname = driver.find_element_by_id("wpDestFile")
   fname.send_keys(f"T--MADRID_UCM--{str('~'.join(fpath.parts))}")
   upload = driver.find_element_by_name("wpUpload")
   v = input("Upload?(Y/N): ") if interactive else 'Y'
   if v == 'Y':
      upload.click()
      new_links_file.write(f"https://2019.igem.org/File:T--MADRID_UCM--{str('~'.join(fpath.parts))}\n")

def upload_page(driver, fpath):

   fpathclean = fpath.with_suffix("")
   driver.get(f"https://2019.igem.org/wiki/index.php?title=Team:MADRID_UCM/{str(fpathclean)}&action=edit")
   textarea = driver.find_element_by_id("wpTextbox1")
   textarea.clear()
   write_file(driver, textarea, fpath)
   save = driver.find_element_by_id("wpSave")
   s = input("Save page?(Y/N): ")
   if s == 'Y':
      save.click()

def print_out(s):
   if interactive:
      print(s)

if __name__ == "__main__":


   WEB_DIR = os.path.abspath(os.curdir)+'/'
   if (len(sys.argv) < 3):
      print(f"Usage: {sys.argv[0]} <web_dir> <glob> <options>")

   path = sys.argv[1]
   if (os.path.isdir(path)):
      WEB_DIR = path if os.path.isabs(path) else WEB_DIR+path

   only_check = False
   html = False
   replace = False
   if("-c" in sys.argv):
      only_check = True
   if("-n" in sys.argv):
      interactive = False
   if("-h" in sys.argv):
      html = True
   if("-r" in sys.argv):
      replace = True

   if WEB_DIR[-1] != '/':
      WEB_DIR += "/"
   print(WEB_DIR)

   p = Path(WEB_DIR)

   if not only_check:
      driver = Firefox()
      driver.implicitly_wait(20)
      login(driver)
      sleep(10)
   
   last_file_found = True
   last_file = ""
   #if os.path.isfile(LOG_FILE):
   #   last_file_found = False
   #   log = open(LOG_FILE, "r")
   #   last_file = log.read()
   #   log.close()

   if "-f" in sys.argv:
      ups = (WEB_DIR / Path(sys.argv[sys.argv.index("-f")+1])).open()
      paths = list(map(lambda x: Path(WEB_DIR+x[:-1]), ups))
      ups.close()
   else:
      paths = list(filter(Path.is_file, p.glob(sys.argv[2])))

   new_links_file = open("new_links.txt", "w")
   links_file = open("links.txt", "r")
   links = links_file.read().split("\n")
   links_file.close();
   size = int(int(len(paths) / 4))
   thread_path = []

   for i in range(0, len(paths), max(1,size)):
       thread_path.append(paths[i:i+size])

   def uploads(paths,driver,replace,html):

      for f in paths:
         relf = f.relative_to(WEB_DIR)

         #if not last_file_found:
         #   if str(relf) == last_file:
         #      last_file_found = True
         #      print("Initiating...")
         #   else:
         #      continue

         try:
            if relf.suffix == '.html':
               if html:
                  print(f"Uploading page {str(relf)}")
                  if not only_check:
                     upload_page(driver, relf)
            else:
               if 'js.txt' in relf.name or 'css.txt' in relf.name or 'orig.txt' in relf.name:
                  if replace or not check_template_exists(relf):
                     print_out(f"Uploading template {str(relf)}")
                     if not only_check:
                        upload_template(driver, relf)
                  else:
                     print_out(f"Skipping existing template {str(relf)}")
               else:
                  if replace or not check_file_exists(relf):
                     print_out(f"Uploading file {str(relf)}")
                     if not only_check:
                        upload_file(driver, relf)
                  else:
                     print_out(f"Skipping existing file {str(relf)}")

         except Exception as e:
            print(e)
            log = open(LOG_FILE, "w")
            log.write(str(relf))
            log.close()
            driver.quit()
            sys.exit()

   threads = []
   thread1 = threading.Thread(target = uploads, args=(thread_path[0],driver,replace,html))

   if len(thread_path) > 1:
        thread2 = threading.Thread(target = uploads, args=(thread_path[1],driver,replace,html))
   
        if len(thread_path) > 2:

                thread3 = threading.Thread(target = uploads, args=(thread_path[2],driver,replace,html))
               
                if len(thread_path) > 3:
                    thread4 = threading.Thread(target = uploads, args=(thread_path[3],driver,replace,html))
                    threads.extend((thread1,thread2,thread3,thread4))
                else:
            	    threads.extend((thread1,thread2,thread3))
        else:
        	threads.extend((thread1,thread2))
        
        for t in threads:
            t.start()

        for t in threads:
            t.join()
            
   else:
    	thread1.start()
    
   new_links_file.close()
