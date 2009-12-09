#!/usr/bin/python
# -*- coding: utf-8 -*-

# Runs one match and return program-oriented (second parameter) score

import random, sys, os, stat
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile


def make_parameters_file():
    tmp = NamedTemporaryFile(prefix='params-', dir='.', delete=False)
    for line in sys.stdin:
        print >>tmp, line,
    tmp.close()
    return tmp.name

def make_wrapper(program, parameters):
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

def clean_up():
    os.remove(wrapper)
    os.remove(parameters)

def match(base_program, program):
    first = random.randint(0, 1) #which program is about to play first
    programs = [base_program, program]
    judge = Popen(
        ['./judge-static', '-s', '-P 0', '-i', 'plik_11.txt',
            programs[first], programs[1 - first]],
        stdout=PIPE)
    result = judge.wait()

    if result != 0:
        print >> sys.stderr, 'match.py: judge-static returned error'
        clean_up()
        exit(-1)

    line = judge.stdout.readlines()[-1].split('=')
    score = int(line[1].split(' ')[0])
    #time_used = int(line[3].split(' ')[0])
    if first == 0:
        return score
    else:
        return 1 - score

if len(sys.argv) != 3:
    print >> sys.stderr, 'USAGE: match.py <base_program> <program>'
    exit(-1)

base_program = sys.argv[1]
program = sys.argv[2]

parameters = make_parameters_file()
wrapper = make_wrapper(program, parameters)

print match(base_program, wrapper)
clean_up()