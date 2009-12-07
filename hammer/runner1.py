#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

#TODO: parametry (pliki-gracze)
#TODO: losowanie kolejnosci graczy
       #import random
       #random.randint(0,1)

	#runner ma za zadanie zwrocic kod bledu z przedzialu 0..1 - liczbe wygranych testowanego
	#jest wywolywany z hammer'a, mozna przekazac mu tam jakies parametry...

pipe = os.pipe()
fd1 = os.dup(1)
os.close(1)
os.dup2(pipe[1],1)		
		#random-engine == random-engine2, ale - oba sa seed'owane tylko 'time(0)'...  stad moga byc dziwne wyniki rozgrywek
os.system("./judge-static -s -P 0 -T 100000 -i plik_11.txt ./random-engine ./random-engine2  | tail -n 1 | cut \"-d \" -f 2 | cut -c 7")
result = os.read(pipe[0],100)
#print "result: " + result 
os.close(1)
os.dup2(fd1, 1)
os.close(fd1)
os.close(pipe[0])
os.close(pipe[1])
exit(int(result))

#exit(random.randint(0,1),1)

