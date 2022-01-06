#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import CSP
from arc_consistency import ac3, ac4

def forward_checking(csp: CSP.CSP, level: int, varId, var) -> bool:
    # Forward-checking
    contradiction = False
    for c in csp.all_associated_constrs(varId):
        contradiction = not c.propagate_assignment(var, csp.assignments, level)
        # contradiction = rue if constraint c cannot be verified for current assignment
        if contradiction:
            return contradiction
    return contradiction

def bt(csp: CSP.CSP, varId) -> bool:
    """ Return True, if the assignment of the given variable leads to a contradiction. """
    for c in csp.all_associated_assigned_constrs(varId):
        if not c.is_feasible(csp.assignments[c.var1.id], csp.assignments[c.var2.id]):
            return True
    return False


def backtracking(csp: CSP.CSP, level: int) -> bool:
    """A depth first backtracking algorithm.

    Args:
        csp (CSP.CSP): a CSP solver
        level (int) : actual level in tree

    Returns:
        (bool): True if the partial assignment (stored in csp) is feasible, False otherwise
    """
    if csp.assignments is None:
        raise AttributeError("Missing partial assignment : csp.assignments has not been initialized")

    print("level =", level, "assignments : ")
    for var in csp.vars:
        v = csp.assignments[var.id]
        if v is not None:
            print(var.name, " = ", v)

    if csp.nb_assigned == csp.nbVars:
        return True

    csp.exploredNodes += 1  # arrived at a new node

    # Propagate domain updates to (potential) children nodes
    for var_to_update in csp.vars:
        var_to_update.current_dom_size[level + 1] = var_to_update.current_dom_size[level]

    # pick up a variable
    varId = csp.select_unassigned_varId(level)
    var = csp.vars[varId]
    print("picked var : {}, current domain : {}".format(var.name, var.dom(level)))
    var.level = level
    csp.nb_assigned += 1

    if csp.param["look-ahead"]["AC3"] : 
        ac3(csp, level)

    if csp.param["look-ahead"]["AC4"] : 
        ac4(csp, level)

    # try values affections
    values_order = csp.select_values(varId, level)
    for value in values_order:
        csp.assignments[varId] = value
        csp.vars[varId].assignment = value

        contradiction = False

        if csp.param["look-ahead"]["BT"] : 
            contradiction = bt(csp, varId)

        if csp.param["look-ahead"]["FC"] : 
            contradiction = forward_checking(csp, level, varId, var)

        if not contradiction:
            if backtracking(csp, level + 1):
                return True
            # else contradiction found further down the tree, so try another value
            print("backtracking from value {} for variable {}".format(csp.assignments[varId], var.name))

        # A contradiction was found, reset domains and try a different value
        for var_to_update in csp.vars:
            var_to_update.current_dom_size[level + 1] = var_to_update.current_dom_size[level]

    # All values for selected variable lead to a contradiction, current partial assignment is not feasible
    var.level = -1
    csp.assignments[varId] = None
    csp.vars[varId].assignment = None
    csp.nb_assigned -= 1

    return False
