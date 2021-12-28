#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import numpy as np
import time


VARIABLES_SELECTION = ["arbitrary", "smallest_domain", "most_constrained", "dom_over_constr"]
VALUES_SELECTION = ["arbitrary", "ascending", "descending", "most_supported"]


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
        self.current_dom_size = None

    def __repr__(self):
        return "variable {}".format(self.name)

    def dom(self, level: int = -1):
        """Returns the domain of the variable for the specified depth level during backtrack search

        Args:
            level (int): Depth level (on the current branch). If level=-1, returns the initial domain of the variable.

        Returns:
            (list): list of all remaining possible values at given level
        """
        if level == -1:
            return self._dom[:]
        return self._dom[:self.current_dom_size[level]]

    def remove_value(self, value, level):
        last = self.current_dom_size[level] - 1
        to_remove = -1
        for i in range(last + 1):
            if self._dom[i] == value:
                to_remove = i
                break
        
        if to_remove == -1:
            raise ValueError("Value {} not found in variable {}'s domain at level {}".format(value, self.name, level))
        self._dom[to_remove], self._dom[last] = self._dom[last], self._dom[to_remove]
        self.current_dom_size[level] -= 1


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
                elif funCompatible(var1.id, var2.id, a, b):
                    self.feasibleTuples.add((a, b))

    def __repr__(self):
        return "constraint {0} : ({1}, {2})".format(self.id, self.var1.name, self.var2.name)

    def is_feasible(self, value1: int, value2: int):
        """ Return True if the given assigned values are satisfied by current constraint, False otherwise. """
        return (value1, value2) in self.feasibleTuples

    def reverse(self):
        """Returns a copied constraint where first and second variable roles are inversed

        Returns:
            (Constraint): the reversed constraint
        """
        return Constraint(
            id=-self.id,
            var1=self.var2, var2=self.var1,
            funCompatible=lambda x, y, a, b: self.is_feasible(b, a)
        )

    def propagate_assignment(self, assigned_var, assignments, level):
        """After one of its constraints was assigned a value, eliminated infeasible values from the second one's domain

        Args:
            assigned_var (Variable): The variable which was assigned a value during backtracking
            assignments (list): Link between a variable's id and its assigned value
            level (int): Depth on the current branch in backtracking

        Returns:
            (bool): True if the constraint is still feasible after reducing the second variable's domain, False otherwise
        """
        if assigned_var == self.var1:
            var_to_check = self.var2
        elif assigned_var == self.var2:
            var_to_check = self.var1
        else:
            raise ValueError("Variable {} not in constraint {} (should be {} or {})".format(
                    assigned_var.name, self.id, self.var1.name, self.var2.name
                ))

        if assignments[assigned_var.id] is None:
            raise ValueError("Variable {} should have an assigned value".format(assigned_var.name))

        contradiction = False

        if assignments[var_to_check.id] is None:
            for value in var_to_check.dom(level):

                assignments[var_to_check.id] = value
                feasible = self.is_feasible(assignments[self.var1.id], assignments[self.var2.id])
                assignments[var_to_check.id] = None

                if not feasible:
                    var_to_check.remove_value(value, level + 1)

                    if var_to_check.current_dom_size[level + 1] == 0:
                        contradiction = True
                        break
                        
        return not contradiction


class CSP(object):
    """ Implementation of an integer Constraint Satisfaction Programming Solver.
    For the sake of simplicity, all attributes are public.
    """

    def __init__(self, vars=None, constrs=None):
        """Initialize a CSP.

        Args:
            vars (list of Variable): lis of problem's variables
            constrs (list of Constraint): list of problem's constraints
        """
        if vars is None:
            vars = []
        if constrs is None:
            constrs = []

        self.nbVars = len(vars)
        self.vars = vars  # list of variables

        self.nbConstrs = len(constrs)
        self.constrs = constrs  # list of constraints

        self.matrixIncident = None # matrixIncident[var1][var2] = True, if var1 and var2 are linked by a constraint
        self.supportedValCount = None

        self.param = dict() # parameters settings
        self.__init_parameters()

        # Used for solving
        self.assignments = None
        self.nb_assigned = None
        self.exploredNodes = 0
        self.exploreTime = 0
        self.isFeasible = False
    
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
    
    def __init_matrix_incidency_supported_values_counter(self):
        """ Initialize a binary incidency matirx that mat[var1][var2] = True, if var1 and var2 are linked with a constraint. """
        self.matrixIncident = [[False for _ in range(self.nbVars)] for _ in range(self.nbVars)] 
        self.supportedValCount = [{val : 0 for val in self.vars[id].dom(-1)} for id in range(self.nbVars)]
        
        for c in self.constrs:
            self.matrixIncident[c.var1.id][c.var2.id] = True
            self.matrixIncident[c.var2.id][c.var1.id] = True
            for a in c.var1.dom(0):
                for b in c.var2.dom(0):
                    if c.is_feasible(a, b):
                        nb = self.supportedValCount[c.var1.id][a]
                        self.supportedValCount[c.var1.id].update({a : nb+1})
                        nb = self.supportedValCount[c.var2.id][b]
                        self.supportedValCount[c.var2.id].update({b : nb+1})
    
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
        min_dom_size = float('inf')
        for i in range(self.nbVars):
            if self.assignments[i] is None and self.vars[i].current_dom_size[level] < min_dom_size:
                id = i
                min_dom_size = self.vars[i].current_dom_size[level]

        if id < 0 or min_dom_size <= 0:
            raise ValueError("Selected variable at level {} is {} and its domain cardinality equals {}.".format(
                level, id, min_dom_size
            ))

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
        isolated = list()  # variables have no constraint
        for i in candidates:
            cardConstr = self.__count_related_constraints(i)
            if cardConstr == 0:
                isolated.append(i)
            elif (self.vars[i].current_dom_size[level] / cardConstr) < ratio:
                ratio = (self.vars[i].current_dom_size[level]) / cardConstr
                id = i
        if id < 0:
            return random.choice(isolated)
        else:
            return id

    def select_values(self, varId: int, level=-1):
        if self.param["value"] == VALUES_SELECTION[0]:
            return self.__select_values_arbitrary(varId, level)
        if self.param["value"] == VALUES_SELECTION[1]:
            return self.__select_values_in_ascending_order(varId, level)
        if self.param["value"] == VALUES_SELECTION[2]:
            return self.__select_values_in_descending_order(varId, level)
        if self.param["value"] == VALUES_SELECTION[3]:
            return self.__select_values_most_supported_order(varId, level)
        raise ValueError("Value selection parameter error : {}.".format(self.param["value"]))

    def __select_values_arbitrary(self, varId: int, level=-1):
        """ Select values arbitrarily. """
        values_order = self.vars[varId].dom(level)[:]
        np.random.shuffle(values_order)
        return values_order
    
    def __select_values_in_ascending_order(self, varId: int, level=-1):
        """ Select values in ascending order. """
        values_order = sorted(self.vars[varId].dom(level))
        return values_order

    def __select_values_in_descending_order(self, varId: int, level=-1):
        """ Select values in descending order. """
        values_order = sorted(self.vars[varId].dom(level), reverse=True)
        return values_order

    def __select_values_most_supported_order(self, varId: int, level=-1):
        """ Select values most supported. """
        return list(filter(lambda val : val in self.vars[varId].dom(level), 
                sorted(self.supportedValCount[varId].keys(), 
                    key=lambda x: self.supportedValCount[varId][x], reverse= True)))

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

    def vars_allDiff(self):
        pass

    def display(self):
        for c in self.constrs:
            print(c)
            for (a, b) in c.feasibleTuples:
                print("(", a, ", ", b, ")")

    def solve(self):
        """Solves the CSP with a backtracking algorithm. Final variable values are stored in self.assignments.

        Returns:
            (bool): True if the CSP admits at least one feasible solution, False otherwise.
        """
        from backtrack import backtracking  # to avoid circular imports
        from arc_consistency import ac3

        # setup
        self.assignments = [None for _ in range(self.nbVars)]
        self.nb_assigned = 0

        for var in self.vars:
            var.current_dom_size = var.dom_size * np.ones(self.nbVars + 1, dtype=int)

        # Actual solve
        ac3(self)

        self.__init_matrix_incidency_supported_values_counter()
        #print("supportedValCount : {}. ".format(self.supportedValCount))

        start = time.time()

        self.isFeasible = backtracking(self, 0)

        end = time.time()
        self.exploreTime = end - start
        
        return self.isFeasible
