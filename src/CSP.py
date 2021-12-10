#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random

VARIABLES_SELECTION = ["arbitrary"] # d'autres possibilités à compléter
VALUES_SELECTION = ["arbitrary"] # d'autres possibilités à compléter


""" Implementation of a variable object. For the sake of simplicity, all attributes are public.
"""
class Variable(object):

    def __init__(self, id : int, name : str, domMin : int, domMax : int): #, domFun):
        """ Initialize a variable."""
        self.id = id
        self.name = name #facultatif

        self.domMin = domMin
        self.domMax = domMax
        self.domEnum = set(range(domMin, domMax+1)) # domaine énumérée, l'ens élément finis
        #self.domFun = domFun # domaine définie par une fonction
        self.level = -1
        self.assigned = False



""" Implementation of a constraint object. For the sake of simplicity, all attributes are public.
"""
class Constraint(object):

    def __init__(self, id:int, var1:Variable, var2 : Variable, funCompatible=None):
        """ Initialize a constraint."""
        self.id = id
        self.var1 = var1
        self.var2 = var2

        self.feasibleTuples = set() # l'ensemble couples admissibles
        for a in var1.domEnum: 
            for b in var2.domEnum : 
                if funCompatible==None: self.feasibleTuples.add((a, b))
                elif funCompatible(a, b): self.feasibleTuples.add((a, b))


    def __repr__(self):
        return "constraint {0} : ({1}, {2})".format(self.id, self.var1.name, self.var2.name)


    def is_feasible(self, value1: int, value2: int):
        """ Return True if the given assigned values are satisfied by current constraint, False otherwise. """
        return (value1, value2) in self.feasibleTuples



""" Implementation of an integer Constraint Satisfaction Programming Solver. 
For the sake of simplicity, all attributes are public.
"""
class CSP(object):

    def __init__(self, vars=list(), constrs=list()):
        """ Initialize a CSP."""
        self.nbVars = len(vars)
        self.vars = vars # list of variables

        self.nbConstrs = len(constrs)
        self.constrs = constrs # list of constraints


    def add_variable(self, name : str, domMin : int, domMax : int):
        """ Create and add a new variable to CSP. """
        self.vars.append(Variable(self.nbVars, name, domMin, domMax))
        self.nbVars += 1


    def add_constraint(self, var1: int, var2 : int, funCompatible=None):
        """ Create and add a new constraint to CSP. """
        self.constrs.append(Constraint(self.nbConstrs, self.vars[var1], self.vars[var2], funCompatible))
        self.nbConstrs += 1


    def add_unairy_constraint(self, varId : int, subDom : list):
        """ Add a domain constraint on variable varId. """
        for v in subDom:
            if v not in self.vars[varId].domEnum: print("ERROR : ", v , "not compatible ! ")

        self.vars[varId].domEnum = set(subDom.sort())


    def select_varId_arbitrary(self, exception:list):
        """ Select an unassigned variable arbitrarily, where 'exception' is the list of assigned variables' ids. """
        if len(exception)==0: return random.choice(range(self.nbVars))
        listID = list(filter(lambda x : x not in exception, range(self.nbVars))) # list of remaining vars' id
        return random.choice(listID)


    def select_arbitrary_value(self, varId:int):
        """ Given a variable, select a value arbitrarily. """
        return random.choice(self.vars[varId].domEnum)


    def all_associated_constrs(self, varId: int):
        """ Return all constraints containing the given variable. """
        return list(filter(lambda c : c.var1.id == varId or c.var2.id == varId, self.constrs))


    def all_associated_assigned_constrs(self, varId: int):
        """ Return all constraints containing the given variable, and the other variable is also assigned. """
        return list(filter(lambda c : c.var1.assigned==True and c.var2.assigned==True, 
            self.all_associated_constrs(varId)))


    def is_feasible(self):
        pass
        

    def vars_allDiff(self):
        pass


    def display(self):
        for c in self.constrs:
            print(c)
            for (a, b) in c.feasibleTuples:
                print("(", a, ", ", b, ")")






