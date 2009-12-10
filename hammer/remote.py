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

   def __repr__(self):
      return remoteMachines

   def Connect(self, password):
      count = 0
      while (True):
         self.semaphore.acquire()
         self.lock.acquire()
         machine = self.remoteMachines.pop(0)
         self.lock.release()

         count = count + 1
         if count > 30:
            raise Exception("could not establish a ssh connection")

         ssh_newkey = "Are you sure you want to continue connecting"
         ssh = pexpect.spawn("ssh " + machine)

         i = ssh.expect([ssh_newkey, "Password:", "\$", pexpect.TIMEOUT, pexpect.EOF])
         if i == 0:
            ssh.sendline("yes")
            i = ssh.expect([ssh_newkey, "Password:", "\$", pexpect.TIMEOUT, pexpect.EOF])
         if i == 1:
            ssh.sendline(password)     # password required
            return ssh
         if i == 2:              # connected
            return ssh
         else:
            self.lock.acquire()
            self.remoteMachines.append(machine)
            self.lock.release()
            self.semaphore.release()

   def Prepare(self, ssh, path):
      ssh.expect("\$")
      ssh.setecho(False)
      ssh.sendline("cd " + path)
      ssh.readline() # shouldn't be necessary, but is, and I have no idea as to why

   def Execute(self, ssh, parameterList, engines):
      ssh.sendline("./match.py " + engines[0] + " " + engines[1])
      ssh.readline()

      for parameter in parameterList:
         ssh.sendline(parameter)
         ssh.readline()

      ssh.sendline("")
      ssh.readline()
      r = ssh.readline()
      print r

      if (split('\r', r)[0] == "0"):
         result = (0, 1)
      else:
         result = (1, 1)

      return result

#from parser import Parser

#rmh = RemoteMachinesHub(Parser().ParseRemoteMachines())
#print rmh.Execute(Parser().ParseParameters()[0])

