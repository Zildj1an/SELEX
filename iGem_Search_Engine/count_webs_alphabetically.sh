#!/bin/bash

# Prints the alphabetical distribution of teams by year.
# Usage: ./alpha <year>
# Pablo Villalobos

readonly URL="urls_to_2019"

if [ $1 -gt 2019 ] || [ $1 -lt 2008 ]
then
  echo Invalid year
  exit 1
fi

LANG="en_US.UTF-8" # Needed for printf
total=$(cat $URL | grep "$1\." | grep "Team\:" | wc -l)

echo "Year $1, total urls: $total"

for letter in {A..Z} {a..z}
  do
    num=$(cat $URL | grep "$1\." | grep "Team:$letter" | wc -l)
    rel=$(bc <<< "scale=1; 100*$num/$total")
    if [ $(bc <<< "$rel>0.001") -eq 1 ]
    then
      echo -n "$letter: "
      printf '%.3f%b\t' $rel '%'
      rel=$(bc <<< "$rel*3")
      for i in $(seq 1 $rel)
        do
          echo -n \#
        done
      echo
    fi
  done
