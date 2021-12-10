#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from CSP import *

def backtracking(csp: CSP, assignments: dict, level: int):
    """ A deep first backtracking algorithm.

    Args:
        csp (CSP): a CSP solver
        assignments (dict): variable's id => affected value
        level (int) : actual level in tree
    """
    print("level=", level, "assignments : ")
    for id,v in assignments.items(): print(csp.vars[id].name, " = ", v)

    if len(assignments) == csp.nbVars: return assignments

    # pick up a variable
    varId = csp.select_varId_arbitrary(assignments.keys()) 
    print("picked var : ", csp.vars[varId].name)
    csp.vars[varId].level = level
    csp.vars[varId].assigned = True

    # try values affections
    values = list(csp.vars[varId].domEnum)
    while(len(values) > 0):
        v = random.choice(values)
        values.remove(v)

        d = {varId : v}
        assignments.update(d)

        OK = True
        for c in csp.all_associated_assigned_constrs(varId):
            if not c.is_feasible(assignments[c.var1.id], assignments[c.var2.id]):
                OK = False
        
        if OK: 
            return backtracking(csp, assignments, level+1)
    
    csp.vars[varId].level = -1
    csp.vars[varId].assigned = False
