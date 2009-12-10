#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append("./pexpect-2.3")
import pexpect
import threading
from re import split

class RemoteMachinesHub:
   # essentially a list of remote machines' addresses
   # the semaphore prohibits form lunching ssh on a same
   # machine more than once at a time
   # the lock is a standard mutex for the list
   def __init__(self, _remoteMachines):
      self.remoteMachines = _remoteMachines
      self.lock = threading.Lock()
      self.semaphore = threading.Semaphore(len(self.remoteMachines))

      #tmp = os.popen("pwd")
      #self.path = split('\n', tmp.readline())[0]
      #tmp.close()
      self.path = "~/SIG/Hex/hammer"

   def __repr__(self):
      return remoteMachines

   def Connect(self):
      self.semaphore.acquire()
      self.lock.acquire()
      self.machine = self.remoteMachines.pop(0)
      self.lock.release()

      ssh_newkey = "Are you sure you want to continue connecting"
      ssh = pexpect.spawn("ssh " + self.machine)

      i = ssh.expect([ssh_newkey, "Password:", "\$", pexpect.TIMEOUT, pexpect.EOF])
      if i == 0:
         ssh.sendline("yes")
         i = ssh.expect([ssh_newkey, "Password:", "\$", pexpect.TIMEOUT, pexpect.EOF])
      if i == 1:
         ssh.sendline("")     # password required
         return ssh
      if i == 2:              # connected
         return ssh
      else:
         self.lock.acquire()
         self.remoteMachines.append(self.machine)
         self.lock.release()
         self.semaphore.release()
         return None

   def Execute(self, parameterList):
      ssh = None
      while (ssh == None):
         ssh = self.Connect()

      #print "connected"

      ssh.setecho(False)
      ssh.sendline("cd " + self.path)
      ssh.readline() # shouldn't be necessary but is
      ssh.sendline("./match.py ./engine ./engine")
      ssh.readline()

      for parameter in parameterList:
         ssh.sendline(parameter)
	 ssh.readline()

      ssh.sendline("")
      ssh.readline()

      #print ssh.readline()
      #print ssh.readline()

      if (split('\r', ssh.readline())[0] == "0"):
         result = (0, 1)
      else:
         result = (1, 1)

      ssh.close()

      self.lock.acquire()
      self.remoteMachines.append(self.machine)
      self.lock.release()
      self.semaphore.release()

      return result

from parser import Parser

rmh = RemoteMachinesHub(Parser().ParseRemoteMachines())
print rmh.Execute(Parser().ParseParameters()[0])
