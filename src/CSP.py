#!/usr/bin/env python3
# -*- coding: utf-8 -*-


VARIABLES_SELECTION = ["arbitrary"] # d'autres possibilités à compléter
VALUES_SELECTION = ["arbitrary"] # d'autres possibilités à compléter

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
        #def domFun():
        #    pass
        #self.domFun = domFun # domaine définie par une fonction

    def __init__(self, id : int, name : str, domMin : int, domMax : int): #, domFun):
        """ Initialize a variable."""
        self.id = id
        self.name = name #facultatif

        self.domMin = domMin
        self.domMax = domMax
        self.domEnum = set(range(domMin, domMax+1)) # domaine énumérée, l'ens élément finis
        #self.domFun = domFun # domaine définie par une fonction


    
""" Implementation of a constraint object. For the sake of simplicity, all attributes are public.
"""
class Constraint(object):
    def __init__(self):
        """ Initialize an empty constraint."""
        self.var1 = Variable()
        self.var2 = Variable()

        self.feasibleTuples = set() # l'ensemble couples admissibles

    def __init__(self, var1:Variable, var2 : Variable):
        """ Initialize a constraint."""
        self.var1 = var1
        self.var2 = var2

        self.feasibleTuples = set() # l'ensemble couples admissibles
        for a in var1.domEnum: 
            for b in var2.domEnum : self.feasibleTuples.add((a, b))

    def __repr__(self):
        return "constraint ({0}, {1})".format(self.var1.name, self.var2.name)


""" Implementation of an integer Constraint Satisfaction Programming Solver. 
For the sake of simplicity, all attributes are public.
"""
class CSP(object):
    def __init__(self):
        """ Initialize an empty CSP."""
        self.nbVars = 0
        self.vars = list() # list of variables

        self.nbConstrs = 0
        self.constrs = list() # list of constraints

    def __init__(self, nbVars : int, vars : list, nbConstrs : int, constrs : list):
        """ Initialize a CSP."""
        self.nbVars = nbVars
        self.vars = vars # list of variables

        self.nbConstrs = nbConstrs
        self.constrs = constrs # list of constraints

    def add_variable(self, var:Variable):
        """ Add a variable to CSP. """
        self.nbVars += 1
        self.vars.append(var)

    def add_constraint(self, constr:Constraint):
        """ Add a constraint to CSP. """
        self.nbConstrs += 1
        self.constrs.append(constr)



