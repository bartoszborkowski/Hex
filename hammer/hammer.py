#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from math import sqrt
import operator
import random
import signal
import os
import threading
import thread
import time
import sys
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile

ALPHA = 3.0		#alfa 4 UCB
PRIOR = (1,2)		#priot 4 UCB	(wins, visits)

THREADS_NUM = 3

class RemoteMachine:	#TODO: maybe simple string will be better...
			#or we will make it contain number of cores of machine...?
	# RemoteMachine holds the name of a remote machine as specified in remote.conf
	name = ""
	def __init__(self, _name):
		self.name = _name
	def __repr__(self):
		return "RemoteMachine(" + self.name + ")\n"

class Parser:
	# Parser parses the two files: parameter.conf and remote.conf
	# Parser's main function: Parse returns a pair of lists:
	# the first list is a list of maps "paramName->paramValue"
	# in that list all possible combination of parameter values
	# are held
	# the second in a list of RemoteMachines, where
	# information about all remote machines is held
	def ParseParameters(self):
		paramFile = open('./parameter.conf', 'r')
		paramCmds = []
		paramVals = []
		result = []		#lista map "nazwa->wartosc"
		def ParseParameterList(start):
			result = []
			if (start == len(paramVals) - 1):
				[result.append([i]) for i in paramVals[start]]
			else:
				[result.append(j + [i]) for i in paramVals[start] for j in ParseParameterList(start + 1)]
			return result
		for line in paramFile:
			l = []
			spLine = re.split(' |\n', line)
			paramCmds.append(spLine.pop(0))
			for i in range(len(spLine) - 1):
				l.append(spLine[i])
			paramVals.append(l)
		paramCmds.reverse()
#		print ParseParameterList(0)
		for valList in ParseParameterList(0):
			params = {}
			for i in range(len(paramCmds)):
				params[paramCmds[i]] = valList[i]

			result.append(params)
		paramFile.close()
		return result

	def ParseRemoteMachines(self):
		paramFile = open('./remote.conf', 'r')
		result = []
		for line in paramFile:
			spLine = re.split('\n', line)
			result.append(RemoteMachine(spLine[0]))
		paramFile.close()
		return result

	def Parse(self):
		return (self.ParseParameters(), self.ParseRemoteMachines())

#testingJudge - funkcja z 1arg: mapa "nazwa->wartosc", zwracajaca krotke (liczba_wygranych, liczba_rozgrywek)
def testing_judge(params):
    match = Popen(['./match.py', './engine', './engine'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    for k, v in params.iteritems():
        print >>match.stdin, k, v
    match.stdin.close()
    result = match.wait()

    if result != 0:
        return (0, 0) #match failed

    out = match.stdout.readlines()[0]
    if out[0] == '0':
        return (0, 1)
    else:
        return (1, 1)

class UcbElem: #element of UCB-struct (contains one parameter combination)
    def __init__(self, parameters):
        self.parameters = parameters;
        self.wins = 0
        self.visits = 0
        self.win_rate = 0.0
        self.value = float('inf')
        self.update(PRIOR)

    def update(self, results):
        self.wins = self.wins + results[0]
        self.visits = self.visits + results[1]
        self.win_rate = 1.0 * self.wins / self.visits
        self.value = self.win_rate + ALPHA/sqrt(self.visits)

    def __repr__(self):
        retRepr = "ELEM({"
        for name in self.parameters:
            retRepr = retRepr + name + "->" + self.parameters[name] +" "
        retRepr = retRepr + "} win:%d vis: %d " % (self.wins, self.visits)
        retRepr = retRepr + "(rate:%f) val: %f)\n" % (self.win_rate, self.value)
        return retRepr

class Ucb: #call analyze() few times, and at last: bestElementsList()
    def __init__(self, params):
        self.elements = []
        for param in params:
            elem = UcbElem(param)
            self.elements.append(elem)
        self.visits_total = 0
        self.played_games = 0
        self.lock = threading.Lock()

    def element_to_analyze(self): #assume lock is aquired
        maximum = max(self.elements, key=operator.attrgetter('value')).value
        max_list = filter(lambda(x):(x.value == maximum), self.elements)
        random_idx = random.randint(0, len(max_list) - 1)
        return max_list[random_idx]

    def analyze(self, function): #function must return INT!
        with self.lock:
            self.visits_total += 1
            to_analyze = self.element_to_analyze()

        result_tuple = function(to_analyze.parameters)

        with self.lock:
            self.played_games += result_tuple[1]
            to_analyze.update(result_tuple)

    def best_params_list(self):
        retList = []
        for elem in self.bestElementsList():
            retList.append(elem.parameters)
        return retList

    def best_elements_list(self):
        return sorted(self.elements, key=operator.attrgetter('win_rate'), reverse=True)

    def summary(self, rows_num):
        ret = "total visits: %d (played games: %d)\n" % (self.visits_total, self.played_games)
        for elem in self.best_elements_list()[:rows_num]:
            ret += "\t"
            for paramName in elem.parameters:
                ret += paramName + "=" + elem.parameters[paramName] + ", "
            ret += "\t"
            ret += str(elem.win_rate) + " (wins: " + str(elem.wins) + " / visits: "  + str(elem.visits) + ")  "
            ret += "\n"
        return ret

class UcbThread(threading.Thread):
    def __init__(self, ucb):
        self.ucb = ucb
        self.done = False
        self.lock = threading.Lock()
        threading.Thread.__init__(self)

    def run(self):
        for i in xrange(50):
            with self.lock:
                if self.done:
                    break
            self.ucb.analyze(testing_judge)

    def quit(self):
        with self.lock:
            self.done = True

class ConsoleThread(threading.Thread):
    def __init__(self, ucb, threads):
        threading.Thread.__init__(self)
        self.ucb = ucb
        self.threads = threads
        self.daemon = True

    def run(self):
        while sys.stdin:
            print 'hammer> ',
            line = sys.stdin.readline()
            if line == 'quit\n' or line == 'q\n':
                self.quit()
                break
            else:
                self.stat()

    def stat(self):
        print 'Partial results:', self.ucb.summary(5)

    def quit(self):
        print 'Quit scheduled'
        for thread in self.threads:
            thread.quit()

parser = Parser()
ucb = Ucb(parser.ParseParameters())

ucb_threads = []
for i in xrange(THREADS_NUM):
    thread = UcbThread(ucb)
    thread.start()
    ucb_threads.append(thread)

console = ConsoleThread(ucb, ucb_threads)
console.start()

for thread in ucb_threads:
    thread.join()

print
print "Results:", ucb.summary(10)
