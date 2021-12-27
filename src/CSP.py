#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import numpy as np


VARIABLES_SELECTION = ["arbitrary", "smallest_domain", "most_constrained", "dom_over_constr"]
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

        self.matrixIncident = None # mat[var1][var2] = True, if var1 and var2 are linked by a constraint
        self.param = dict()
        self.__init_parameters()

        # Used for solving
        self.assignments = None
        self.nb_assigned = None
    
    def __init_parameters(self):
        self.param["variable"] = None
        self.param["value"] = None
    
    def set_variable_selection(self, selection=0):
        if selection<0 or selection> len(VARIABLES_SELECTION)-1:
            raise ValueError("The argument variable selection setting {} is invalid.".format(selection))
        self.param.update({"variable" : VARIABLES_SELECTION[selection]})
    
    def set_value_selection(self, selection=0):
        if selection<0 or selection> len(VALUES_SELECTION)-1:
            raise ValueError("The argument value selection setting {} is invalid.".format(selection))
        self.param.update({"value" : VALUES_SELECTION[selection]})  
    
    def __init_matrix_incidency(self):
        """ Initialize a binary incidency matirx that mat[var1][var2] = True, if var1 and var2 are linked with a constraint. """
        self.matrixIncident = [[False for _ in range(self.nbVars)] for _ in range(self.nbVars)]
        for c in self.constrs:
            self.matrixIncident[c.var1.id][c.var2.id] = True
            self.matrixIncident[c.var2.id][c.var1.id] = True
    
    def __count_related_constraints(self, id: int):
        """ Return the number of constraints containing the given variable. """
        return sum(self.matrixIncident[id])

    def add_variable(self, name: str, domMin: int, domMax: int):
        """ Create and add a new variable to CSP. """
        self.vars.append(Variable(self.nbVars, name, domMin, domMax))
        self.nbVars += 1

    def add_constraint(self, var1: int, var2: int, funCompatible=None):
        """ Create and add a new constraint to CSP. """
        self.constrs.append(Constraint(self.nbConstrs, self.vars[var1], self.vars[var2], funCompatible))
        self.nbConstrs += 1

    def select_unassigned_varId(self, level=-1):
        if self.param["variable"] == VARIABLES_SELECTION[0]:
            return self.__select_unassigned_varId_arbitrary()
        if self.param["variable"] == VARIABLES_SELECTION[1]:
            return self.__select_unassigned_varId_smallest_dom(level)
        if self.param["variable"] == VARIABLES_SELECTION[2]:
            return self.__select_unassigned_varId_most_constr()
        if self.param["variable"] == VARIABLES_SELECTION[3]:
            return self.__select_unassigned_varId_dom_over_constr(level)
        raise ValueError("Variable selection parameter error : {}.".format(self.param["variable"]))

    def __select_unassigned_varId_arbitrary(self):
        """ Select an unassigned variable arbitrarily. """
        return random.choice([i for i in range(self.nbVars) if self.assignments[i] is None])

    def __select_unassigned_varId_smallest_dom(self, level=-1):
        """ Select the unassigned variable with smallest domain. """
        id = -1
        domLastIndex = float('inf')
        for i in range(self.nbVars):
            if self.assignments[i] is None and self.vars[i].last[level] < domLastIndex:
                id = i
                domLastIndex = self.vars[i].last[level]
        if id<0 or domLastIndex<0:
            raise ValueError("Selected variable at level {} is {} and its domain cardinality equals {}.".format(
                level, id, domLastIndex+1))
        return id
    
    def __select_unassigned_varId_most_constr(self):
        """ Select the most constrained unassigned variable. """
        id = -1
        nbConstr = -1
        for i in range(self.nbVars):
            if self.assignments[i] is None and self.__count_related_constraints(i) > nbConstr:
                nbConstr = self.__count_related_constraints(i)
                id = i
        return id
    
    def __select_unassigned_varId_dom_over_constr(self, level=-1):
        """ To select the variable leading to a contradiction rapidly, return the variable
            with the smallest ratio |dom|/|constr|. """
        id = -1
        ratio = float('inf')
        candidates = [i for i in range(self.nbVars) if self.assignments[i] is None]
        isolated = list() # variables have no constraint
        for i in candidates:
            cardConstr = self.__count_related_constraints(i)
            if cardConstr == 0:
                isolated.append(i)
            elif ((self.vars[i].last[level]+1)/cardConstr) < ratio:
                ratio = (self.vars[i].last[level]+1)/cardConstr
                id = i
        if id<0:
            return random.choice(isolated)
        else: return id

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
        from backtrack import backtracking  # to avoid circular imports
        from arc_consistency import ac3

        # setup
        self.assignments = [None for _ in range(self.nbVars)]
        self.nb_assigned = 0

        for var in self.vars:
            var.last = (var.dom_size - 1) * np.ones(self.nbVars + 1, dtype=int)

        # Actual solve
        ac3(self)

        self.__init_matrix_incidency()

        return backtracking(self, 0)
