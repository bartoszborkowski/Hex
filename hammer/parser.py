#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import split
from tempfile import NamedTemporaryFile

class Parser:
	# Parser parses the two files: parameter.conf and remote.conf
	# Parser's main function: Parse returns a pair of lists:
	# the first list is a list of maps "paramName->paramValue"
	# in that list all possible combination of parameter values
	# are held
	# the second in a list of RemoteMachines, where
	# information about all remote machines is held
	def __init__(self):
		parameterFiles = []

	def __del__(self):
		for i in self.parameterFiles:
			i.close()

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
			spLine = split(' |\n', line)
			paramCmds.append(spLine.pop(0))
			for i in range(len(spLine) - 1):
				l.append(spLine[i])
			paramVals.append(l)

		paramCmds.reverse()

		for valList in ParseParameterList(0):
			tmp = NamedTemporaryFile(prefix = 'params-', dir = '.')
			for i in range(len(paramCmds)):
				print >> tmp, paramCmds[i], valList[i]
			result.append(tmp)

		paramFile.close()
		self.parameterFiles = result;
		return result

	def ParseRemoteMachines(self):
		paramFile = open('./remote.conf', 'r')
		result = []
		for line in paramFile:
			result.append(split('\n', line)[0])
		paramFile.close()
		return result
