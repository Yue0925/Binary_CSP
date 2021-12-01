#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Implementation of a variable object. For the sake of simplicity, all attributes are public.
"""
class Variable(object):
    def __init__(self):
        """ Initialize an empty variable."""
        self.id = 0
        self.name = str() #facultatif

        self.domMin = 0
        self.domMax = 0
        self.domEnum = set() # domaine énumérée, l'ens élément finis
        #self.domFun = function # domaine définie par une fonction

    def __init__(self, id, name, domMin, domMax, domEnum):
        """ Initialize a variable."""
        self.id = id
        self.name = name #facultatif

        self.domMin = domMin
        self.domMax = domMax
        self.domEnum = domEnum # domaine énumérée, l'ens élément finis
        #self.domFun = function # domaine définie par une fonction


    
""" Implementation of a constraint object. For the sake of simplicity, all attributes are public.
"""
class Constraint(object):
    def __init__(self):
        """ Initialize an empty constraint."""
        self.var1 = Variable()
        self.var2 = Variable()

        self.feasibleTuples = set() # l'ensemble couples admissibles

    def __init__(self, var1, var2, feasibleTuples):
        """ Initialize a constraint."""
        self.var1 = var1
        self.var2 = var2

        self.feasibleTuples = feasibleTuples # l'ensemble couples admissibles


""" Implementation of an integer Constraint Satisfaction Programming Solver. 
For the sake of simplicity, all attributes are public.
"""
class CSP(object):
    def __init__(self):
        """ Initialize an empty CSP."""
        self.nbVars = 0
        self.vars = list() # list of variables

        self.nbConsts = 0
        self.consts = list() # list of constraints

    def __init__(self, nbVars, vars, nbConsts, consts):
        self.nbVars = nbVars
        self.vars = vars # list of variables

        self.nbConsts = nbConsts
        self.consts = consts # list of constraints



