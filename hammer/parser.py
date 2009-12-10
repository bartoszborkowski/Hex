#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import split
from tempfile import NamedTemporaryFile

class Parser:
   # Parser parses the two files: parameter.conf and remote.conf

   def ParseParameters(self):
      # returnes a list of lists of strings: "set_parameter_name parameter_value"
      paramFile = open('./parameter.conf', 'r')
      paramCmds = []
      paramVals = []
      result = []

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
         parameterList = []
         for i in range(len(valList)):
            parameterList.append(paramCmds[i] + ' ' + valList[i])
         result.append(parameterList)

      paramFile.close()
      return result

   def ParseRemoteMachines(self):
      # returns a list of strings: "remote_machine_name"
      paramFile = open('./remote.conf', 'r')
      result = []
      for line in paramFile:
         result.append(split('\n', line)[0])
      paramFile.close()
      return result
