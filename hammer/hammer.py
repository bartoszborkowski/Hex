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
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile

ALPHA = 3.0		#alfa 4 UCB
PRIOR = (1,2)		#priot 4 UCB	(wins, visits)

SAFE_THREADS_NUM = 20	#threads number restrictions
MAX_THREADS_NUM = 20



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

def ParametersTempFile(params):
    tmp = NamedTemporaryFile(prefix='params-', dir='.', delete=False)
    for k, v in params.iteritems():
        print >>tmp, k, v
    tmp.close()
    return tmp.name

#testingJudge - funkcja z 1arg: mapa "nazwa->wartosc", zwracajaca krotke (liczba_wygranych, liczba_rozgrywek)
def testingJudge(paramsValuesMap):
    parameters_file = ParametersTempFile(paramsValuesMap)
    match = Popen(['./match.py', './engine', './engine', parameters_file], stdout=PIPE, stderr=PIPE)
    result = match.wait()
    os.remove(parameters_file)

    if result != 0:
        return (0, 0) #match failed

    out = match.stdout.readlines()[0]
    if out[0] == '0':
        return (0, 1)
    else:
        return (1, 1)

class UCBElem:		#element of UCB-struct (contains one parameter combination)
    parameters = ""	#must be initialized by creator!
    sem = ""
    value = float('inf')
    win_rate = 0
    wins = 0
    visits = 0
    def __init__(self):
	self.sem = threading.Semaphore()
	self.update(PRIOR)		#prior
    def update(self, results):
	self.sem.acquire()	#P()
	self.wins = self.wins + results[0]
	self.visits = self.visits + results[1]
	self.win_rate = 1.0*self.wins / self.visits
	self.value = self.win_rate + ALPHA/sqrt(self.visits)
	self.sem.release()	#V()
    def __repr__(self):
	retRepr = "ELEM({"
	for name in self.parameters:
	    retRepr = retRepr + name + "->" + self.parameters[name] +" "
	retRepr = retRepr + "} win:%d vis: %d " % (self.wins, self.visits)
	retRepr = retRepr + "(rate:%f) val: %f)\n" % (self.win_rate, self.value)
	return retRepr



class UCB:	#call analyze() few times, and at last: bestElementsList()
    elements = "" 	#must be initialized by calling setParams
    visitsTotal = 0
    playedGames = 0

    def setParams(self, new_params):
	self.elements = set([])
	for param in new_params:
	    elem = UCBElem()
	    elem.parameters = param
	    self.elements.add(elem)

    def elementToAnalyze(self):
	maximum = max(self.elements, key=operator.attrgetter('value')).value
	max_list = filter(lambda(x):(x.value==maximum), self.elements)
	if not max_list:  #jesli ktos nam podebral, sprobujemy jeszcze raz...
	    return self.elementToAnalyze()
	random_idx = random.randint(0,len(max_list)-1)
	ret = max_list[random_idx]
	return ret

    def analyze(self, function):	#function must return INT!
	self.visitsTotal += 1
	toAnalyze = self.elementToAnalyze()
	resultTuple = function(toAnalyze.parameters)
	self.playedGames += resultTuple[1]
	toAnalyze.update(resultTuple)

    def bestParamsList(self):
	retList = []
	for elem in self.bestElementsList():
	    retList.append(elem.parameters)
	return retList

    def bestElementsList(self):
	return sorted(self.elements, key=operator.attrgetter('win_rate'), reverse=True)

    def returnBestParamsString(self, rows_num):
	ret = "total visits: %d (played games: %d)\n" % (self.visitsTotal, self.playedGames)
	for elem in self.bestElementsList()[0:rows_num]:
	    ret += "\t"
	    for paramName in elem.parameters:
		ret += paramName + "=" + elem.parameters[paramName] + ", "
	    ret += "\t"
	    ret += str(elem.win_rate) + " (wins: " + str(elem.wins) + " / visits: "  + str(elem.visits) + ")  "
	    ret += "\n"
#	return ret
	ret += "\n"
	return ret


def printHandler(ucb, signum, frame):
    print "\nPARTIAL RESULTS\t" + ucb.returnBestParamsString(6)








	#PRZYKLAD UZYCIA
print "trueTEST & EXAMPLE EXAMPLE EXAMPLE EXAMPLE EXAMPLE EXAMPLE EXAMPLE EXAMPLE & trueTEST "

ucb = UCB()
ucb.setParams(Parser().ParseParameters())

print "\nPO ZALADOWANIU PARAMETROW, A PRZED ROZGRYWKA MECZY:"
print ucb.elements



print "\nSTART ROZGRYWEK (uzyj Ctrl+C, by wypisac wyniki czesciowe):"
signal.signal(signal.SIGINT, lambda x,y: printHandler(ucb, x, y))	#ustawienie obslugi sygnalu Ctrl+C
	    #TODO: obsluga sygnalow przestala dzialac (przez uruchamianie runner1...) :-/


threadsSet = set()
for i in xrange(1000):	#number of 'playouts'
    new_thread = threading.Thread(None, ucb.analyze, None, (testingJudge, ), {})
    threadsSet.add(new_thread)
    new_thread.start()
    if i % 100 == 0:	#sometimes we need to join finished threads
	threadsToRemove = set([])
	for th in threadsSet:
	    if not th.isAlive():
		th.join()
		threadsToRemove.add(th)
	for thR in threadsToRemove:
	    threadsSet.remove(thR)
	print str(i) + "  th:" + str(threading.activeCount()) + "  set:" + str(len(threadsSet))	#XXX

    if MAX_THREADS_NUM < threading.activeCount():#too many threads running, so:
	while SAFE_THREADS_NUM < threading.activeCount():
	    time.sleep(1)


for th in threadsSet:	#finishing
    th.join()



print "\nPO 1tys NIBY_ROZGRYWKACH, posortowane wg najlepszego zestawu parametrow (czyli wg win_rate):"
#print ucb.bestParamsList()	#<<< to jest posortowana lista map "nazwa->wartosc"
print ucb.bestElementsList()	#< a to - lista elementow 'krzewu UCB'

print ucb.returnBestParamsString(5)




print "SYF SYF SYF SYF SYF SYF SYF SYF SYF SYF SYF SYF SYF SYF SYF SYF SYF"
