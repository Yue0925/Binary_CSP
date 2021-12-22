#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

import CSP


def backtracking(csp: CSP.CSP, assignments: dict, level: int):
    """ A deep first backtracking algorithm.

    Args:
        csp (CSP.CSP): a CSP solver
        assignments (dict): variable's id => affected value
        level (int) : actual level in tree
    """
    print("level =", level, "assignments : ")
    for id, v in assignments.items():
        print(csp.vars[id].name, " = ", v)

    if len(assignments) == csp.nbVars:
        return True

    # pick up a variable
    varId = csp.select_varId_arbitrary(assignments.keys())
    var = csp.vars[varId]
    print("picked var : ", csp.vars[varId].name)
    var.level = level
    var.assigned = True

    # try values affections
    values_order = csp.vars[varId].dom.copy()
    np.random.shuffle(values_order)  # TODO : seulement melanger la partie de gauche avec forward checking
    for value in values_order:
        d = {varId: value}
        assignments.update(d)

        OK = True
        for c in csp.all_associated_assigned_constrs(varId):  # TODO : besoin de verifier plus de contraintes avec le forward checking ?
            if not c.is_feasible(assignments[c.var1.id], assignments[c.var2.id]):
                OK = False
                break

        if OK and backtracking(csp, assignments, level + 1):
            return True

    csp.vars[varId].level = -1
    csp.vars[varId].assigned = False
    assignments.pop(varId)
    print("backtracking !")

    return False
