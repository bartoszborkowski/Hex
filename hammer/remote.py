#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import split
from tempfile import NamedTemporaryFile
import os
import threading

from parser import Parser

class RemoteMachinesHub:
	# essentially a list of remote machines' addresses
	# the semaphore prohibits form lunching ssh on a same
	# machine more than once at a time
	# the lock is a standard mutex for the list
	def __init__(self, _remoteMachines):
		self.remoteMachines = _remoteMachines
		self.lock = threading.Lock()
		self.semaphore = threading.Semaphore(len(self.remoteMachines))

		tmp = os.popen("pwd")
		self.path = split('\n', tmp.readline())[0]
		tmp.close()

	def __repr__(self):
		return remoteMachines

	def Connect(self, parameterFile):
	# the second parameter is a temporary file
	# containing a set of commands for the engine
	# TODO: call other programmes than engine
		self.semaphore.acquire()
		self.lock.acquire()
		machine = self.remoteMachines.pop(0)
		self.lock.release()

		parameterFile.seek(0)

		sshPipe = os.popen("ssh " + machine + " \"cd " + self.path + " && ./match.py ./engine ./engine " + parameterFile.name + "\"")

		res = sshPipe.readline()

		try:
			if (res[0] == "0"):
				result = (0, 1)
			else:
				result = (1, 1)
		except IndexError:
			result = (0, 0)

		sshPipe.close()

		self.lock.acquire()
		self.remoteMachines.append(machine)
		self.lock.release()
		self.semaphore.release()

		return result
