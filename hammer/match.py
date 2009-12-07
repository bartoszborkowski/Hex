#!/usr/bin/python
# -*- coding: utf-8 -*-

# Runs one match and return program-oriented (second parameter) score

import random, sys, os, stat
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile

def MakeWrapper(program, parameters):
    wrapper = NamedTemporaryFile(prefix='wrapper-', dir='.', delete=False)

    print >>wrapper, r'''#!/bin/bash
function read_eqs()
{
    for i in `seq $1`; do
        read line
        read line
    done
    cat
}'''
    print >>wrapper,'cat', parameters,'- |',program, '| read_eqs `wc -l <', parameters, '`'

    wrapper.close()
    os.chmod(wrapper.name, stat.S_IRWXU)
    return wrapper.name

def Match(base_program, program):
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

    line = judge.stdout.readlines()[-1].split('=')
    score = int(line[1].split(' ')[0])
    #time_used = int(line[3].split(' ')[0])
    if first == 0:
        return score
    else:
        return 1 - score

if len(sys.argv) != 4:
    print >> sys.stderr, 'USAGE: match.py <base_program> <program> <parameters file>'
    exit(-1)

base_program = sys.argv[1]
program = sys.argv[2]
parameters = sys.argv[3]

wrapper = MakeWrapper(program, parameters)
print Match(base_program, wrapper)
os.remove(wrapper)