#!/usr/bin/python
# -*- coding: utf-8 -*-

import operator
import random
import threading
from math import sqrt
from subprocess import Popen, PIPE

ALPHA = 3.0		#alfa 4 UCB
PRIOR = (1,2)		#priot 4 UCB	(wins, visits)

class UcbElem: #element of UCB-struct (contains one parameter combination)
    def __init__(self, parameters):
        self.parameters = parameters;
        self.wins = 0
        self.visits = 0
        self.win_rate = 0.0
        self.value = float('inf')
        self.update(PRIOR)

    def update(self, results):
        self.wins = self.wins + results[0]
        self.visits = self.visits + results[1]
        self.win_rate = 1.0 * self.wins / self.visits
        self.value = self.win_rate + ALPHA/sqrt(self.visits)

    def __repr__(self):
        retRepr = "ELEM({"
        for name in self.parameters:
            retRepr = retRepr + name + "->" + self.parameters[name] +" "
        retRepr = retRepr + "} win:%d vis: %d " % (self.wins, self.visits)
        retRepr = retRepr + "(rate:%f) val: %f)\n" % (self.win_rate, self.value)
        return retRepr

class Ucb: #call analyze() few times, and at last: bestElementsList()
    def __init__(self, params):
        self.elements = []
        for param in params:
            elem = UcbElem(param)
            self.elements.append(elem)
        self.visits_total = 0
        self.played_games = 0
        self.lock = threading.Lock()

    def element_to_analyze(self): #assume lock is aquired
        maximum = max(self.elements, key=operator.attrgetter('value')).value
        max_list = filter(lambda(x):(x.value == maximum), self.elements)
        random_idx = random.randint(0, len(max_list) - 1)
        return max_list[random_idx]

    def analyze(self, function): #function must return INT!
        with self.lock:
            self.visits_total += 1
            to_analyze = self.element_to_analyze()

        result_tuple = function(to_analyze.parameters)

        with self.lock:
            self.played_games += result_tuple[1]
            to_analyze.update(result_tuple)

    def best_params_list(self):
        retList = []
        for elem in self.bestElementsList():
            retList.append(elem.parameters)
        return retList

    def best_elements_list(self):
        return sorted(self.elements, key=operator.attrgetter('win_rate'), reverse=True)

    def summary(self, rows_num):
        ret = "total visits: %d (played games: %d)\n" % (self.visits_total, self.played_games)
        for elem in self.best_elements_list()[:rows_num]:
            ret += "\t"
            for paramName in elem.parameters:
                ret += paramName + "=" + elem.parameters[paramName] + ", "
            ret += "\t"
            ret += str(elem.win_rate) + " (wins: " + str(elem.wins) + " / visits: "  + str(elem.visits) + ")  "
            ret += "\n"
        return ret