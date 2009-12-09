#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import sys
from subprocess import Popen, PIPE

from parser import Parser
from ucb import Ucb

THREADS_NUM = 3

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
