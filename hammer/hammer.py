#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import sys

from getpass import getpass
from parser import Parser
from remote import RemoteMachinesHub
from subprocess import Popen, PIPE
from ucb import Ucb

THREADS_NUM = 3

class UcbThread(threading.Thread):
    def __init__(self, ucb, hub, path, password):
        self.ucb = ucb
        self.ssh = hub.Connect(password)
        self.ssh = hub.Prepare(self.ssh, path)
        self.done = False
        self.lock = threading.Lock()
        threading.Thread.__init__(self)
        hub.Prepare(self.ssh, path)

    def __del__(self):
        self.ssh.close()

    def run(self):
        while (True):
            with self.lock:
                if self.done:
                    break
            self.ucb.analyze(self.ssh)

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
        print 'Partial results:', self.ucb.summary(10)

    def quit(self):
        print 'Quit scheduled'
        for thread in self.threads:
            thread.quit()

if len(sys.argv) != 4:
    print >> sys.stderr, "USAGE: ./hammer <absolute_path> <engine_1> <engine_2>"
    exit(-1)

path = sys.argv[1]
engines = [sys.argv[2], sys.argv[3]]

password = getpass()

parser = Parser()
hub = RemoteMachinesHub(parser.ParseRemoteMachines())
ucb = Ucb(parser.ParseParameters(), hub, engines)

ucb_threads = []
for i in xrange(THREADS_NUM):
    try:
        thread = UcbThread(ucb, hub, path, password)
        #thread.start()
        ucb_threads.append(thread)
        print "hammer> Thread", i, "connected"
    except Exception as e:
        print >> sys.stderr, "Thread", i, e

console = ConsoleThread(ucb, ucb_threads)
console.start()

for thread in ucb_threads:
    thread.start()

for thread in ucb_threads:
    thread.join()

print
print "Results:", ucb.summary(10)
