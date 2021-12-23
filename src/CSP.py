#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import numpy as np

VARIABLES_SELECTION = ["arbitrary"]  # d'autres possibilités à compléter
VALUES_SELECTION = ["arbitrary"]  # d'autres possibilités à compléter


class Variable(object):
    """ Implementation of a variable object. For the sake of simplicity, all attributes are public.
    """

    def __init__(self, id: int, name: str, domMin: int, domMax: int):  # , domFun):
        """ Initialize a variable."""
        self.id = id
        self.name = name  # facultatif

        self.domMin = domMin
        self.domMax = domMax
        self._dom = list(range(domMin, domMax + 1))  # domaine énumérée, l'ens élément finis
        self.dom_size = len(self._dom)
        # self.domFun = domFun # domaine définie par une fonction
        self.level = -1
        self.assigned = False

        self.last = None

    def __repr__(self):
        return "variable {}".format(self.name)

    def dom(self, level):
        if level == -1:
            return self._dom[:]
        return self._dom[:self.last[level] + 1]

    def remove_value(self, value, level):
        last = self.last[level]
        to_remove = -1
        for i in range(last + 1):
            if self._dom[i] == value:
                to_remove = i
                break
        
        if to_remove == -1:
            raise ValueError("Value {} not found in variable {}'s domain at level {}".format(value, self.name, level))
        self._dom[to_remove], self._dom[last] = self._dom[last], self._dom[to_remove]
        self.last[level] -= 1


class Constraint(object):
    """ Implementation of a constraint object. For the sake of simplicity, all attributes are public.
    """

    def __init__(self, id: int, var1: Variable, var2: Variable, funCompatible=None):
        """ Initialize a constraint."""
        self.id = id
        self.var1 = var1
        self.var2 = var2

        self.feasibleTuples = set()  # l'ensemble couples admissibles
        for a in var1.dom(-1):
            for b in var2.dom(-1):
                if funCompatible is None:
                    self.feasibleTuples.add((a, b))
                elif funCompatible(a, b):
                    self.feasibleTuples.add((a, b))

    def __repr__(self):
        return "constraint {0} : ({1}, {2})".format(self.id, self.var1.name, self.var2.name)

    def is_feasible(self, value1: int, value2: int):
        """ Return True if the given assigned values are satisfied by current constraint, False otherwise. """
        return (value1, value2) in self.feasibleTuples

    def reverse(self):
        return Constraint(
            id=-self.id,
            var1=self.var2, var2=self.var1,
            funCompatible=lambda a, b: self.is_feasible(b, a)
        )


class CSP(object):
    """ Implementation of an integer Constraint Satisfaction Programming Solver.
    For the sake of simplicity, all attributes are public.
    """

    def __init__(self, vars=None, constrs=None):
        """ Initialize a CSP."""
        if vars is None:
            vars = []
        if constrs is None:
            constrs = []

        self.nbVars = len(vars)
        self.vars = vars  # list of variables

        self.nbConstrs = len(constrs)
        self.constrs = constrs  # list of constraints

        # Used for solving
        self.assignments = None
        self.nb_assigned = None

    def add_variable(self, name: str, domMin: int, domMax: int):
        """ Create and add a new variable to CSP. """
        self.vars.append(Variable(self.nbVars, name, domMin, domMax))
        self.nbVars += 1

    def add_constraint(self, var1: int, var2: int, funCompatible=None):
        """ Create and add a new constraint to CSP. """
        self.constrs.append(Constraint(self.nbConstrs, self.vars[var1], self.vars[var2], funCompatible))
        self.nbConstrs += 1

    def add_unairy_constraint(self, varId: int, subDom: list):  # TODO: ne marche plus
        """ Add a domain constraint on variable varId. """
        for v in subDom:
            if v not in self.vars[varId].domEnum:
                print("ERROR : ", v, "not compatible ! ")

        self.vars[varId].dom = subDom

    def select_unassigned_varId_arbitrary(self):
        """ Select an unassigned variable arbitrarily. """
        return random.choice([i for i in range(self.nbVars) if self.assignments[i] is None])

    def select_arbitrary_value(self, varId: int, level=-1):
        """ Given a variable, select a value arbitrarily. """
        return random.choice(self.vars[varId].dom(level))

    def all_associated_constrs(self, varId: int):
        """ Return all constraints containing the given variable. """
        return list(filter(
            lambda c: c.var1.id == varId or c.var2.id == varId,
            self.constrs
        ))

    def all_associated_assigned_constrs(self, varId: int):
        """ Return all constraints containing the given variable, and the other variable is also assigned. """
        return list(filter(
            lambda c: c.var1.assigned and c.var2.assigned,
            self.all_associated_constrs(varId)
        ))

    def is_feasible(self):
        pass

    def vars_allDiff(self):
        pass

    def display(self):
        for c in self.constrs:
            print(c)
            for (a, b) in c.feasibleTuples:
                print("(", a, ", ", b, ")")

    def solve(self):
        self.assignments = [None for _ in range(self.nbVars)]
        self.nb_assigned = 0

        for var in self.vars:
            var.last = (var.dom_size - 1) * np.ones(self.nbVars + 1, dtype=int)
        
        from backtrack import backtracking  # to avoid circular imports
        return backtracking(self, 0)
