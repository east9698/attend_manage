#! /bin/bash

while read line; do

    echo ${line} | sed -e 's/fuga/piyo/g' >> $1
    echo ${line} | /usr/bin/python3.6 /home/east9698/test4.py

done
