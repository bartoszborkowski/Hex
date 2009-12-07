#!/usr/bin/python
# -*- coding: utf-8 -*-

# Runs one match and return program-oriented (second parameter) score

import random, sys
from subprocess import Popen, PIPE
from tempfile import mkstemp

if len(sys.argv) != 3:
    print >> sys.stderr, 'USAGE: match.py <base_program> <program>'
    exit(-1)

base_program = sys.argv[1]
program = sys.argv[2]
first = random.randint(0, 1) #which program is about to play first

programs = [base_program, program]
judge = Popen(
    ['./judge-static', '-s', '-P 0', '-i', 'plik_11.txt',
        programs[first], programs[1 - first]],
    stdout=PIPE)
result = judge.wait()

if result != 0:
    print >> sys.stderr, 'match.py: judge-static returned error'
    exit(-1)

def Extract(line):
    line = line.split('=')
    score = int(line[1].split(' ')[0])
    #time_used = int(line[3].split(' ')[0])
    return score

score = Extract(judge.stdout.readlines()[-1])
if first == 0:
    print score
else:
    print 1 - score