#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import threading

class RemoteMachine:	#TODO: maybe simple string will be better...
			#or we will make it contain number of cores of machine...?
			# Bartek: perhaps this is right and a string will be sufficient
	# RemoteMachine holds the name of a remote machine as specified in remote.conf
	name = ""
	def __init__(self, _name):
		self.name = _name

	def __repr__(self):
		return "RemoteMachine " + self.name + "\n"

	def __str__(self):
		return name

class RemoteMachinesHub:
	# essentially a list of remote machines' addresses
	# the semaphore prohibits form lunching ssh on a same
	# machine more than once at a time
	# the lock is a standard mutex for the list
	remoteMachines = []
	lock = threading.Lock()
	semaphore = threading.Semaphore(1)

	def __init__(self, _remoteMachines):
		self.remoteMachines = _remoteMachines
		self.semaphore = threading.Semaphore(len(self.remoteMachines))

	def __repr__(self):
		return remoteMachines

	def Connect(self):
	# this will have a second argument: parameter
	# which will contain a set of parameters for
	# the match.py programme
	# perhaps also a path to the folder conataining match.py?
	# also it would be nice if ssh would not
	# ask for a password each and every time
	# anyone remembers how's that done?
		self.semaphore.acquire()
		self.lock.acquire()
		machine = self.remoteMachines.pop(0)
		self.lock.release()

		sshPipe = os.popen("ssh " + machine + " cd ~/SIG/Hex/hammer && ./match.py ./engine ./engine ./plik_11.txt")

		res =  sshPipe.readline()

		if (res[0] == "0"):
			result = (0, 1)
		else:
			result = (1, 1)

		sshPipe.close()

		self.lock.acquire()
		self.remoteMachines.append(machine)
		self.lock.release()
		self.semaphore.release()

		return result

		self.semaphore.release()
