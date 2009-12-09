#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

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