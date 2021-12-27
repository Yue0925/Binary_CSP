#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import CSP


def backtracking(csp: CSP.CSP, level: int):
    """ A deep first backtracking algorithm.

    Args:
        csp (CSP.CSP): a CSP solver
        assignments (dict): variable's id => affected value
        level (int) : actual level in tree
    """
    print("level =", level, "assignments : ")
    for var in csp.vars:
        v = csp.assignments[var.id]
        if v is not None:
            print(var.name, " = ", v)

    if csp.nb_assigned == csp.nbVars:
        return True

    # Propagate domain updates to (potential) children nodes
    for var_to_update in csp.vars:
        var_to_update.last[level + 1] = var_to_update.last[level]

    # pick up a variable
    varId = csp.select_unassigned_varId(level)
    var = csp.vars[varId]
    print("picked var : {}, current domain : {}".format(var.name, var.dom(level)))
    var.level = level
    csp.nb_assigned += 1

    # try values affections
    values_order = csp.select_values(varId, level)
    for value in values_order:
        csp.assignments[varId] = value

        # Forward-checking
        contradiction = False
        for c in csp.all_associated_constrs(varId):
            if var == c.var1:
                var_to_check = c.var2
                first = False
            else:
                var_to_check = c.var1
                first = True

            if csp.assignments[var_to_check.id] is None:

                values_to_check = var_to_check.dom(level)
                for b in values_to_check:
                    if first:
                        feasible = c.is_feasible(b, value)
                    else:
                        feasible = c.is_feasible(value, b)

                    if not feasible:
                        var_to_check.remove_value(b, level + 1)
                        if var_to_check.last[level + 1] == -1:
                            contradiction = True
                            break

            # else:  # var_to_check is assigned  # TODO : pas necessaire (?)
            #     if not c.is_feasible(csp.assignments[c.var1.id], csp.assignments[c.var2.id]):
            #         contradiction = True

            if contradiction:
                break

        if not contradiction:
            if backtracking(csp, level + 1):
                return True
            print("backtracking from value {} for variable {}".format(csp.assignments[varId], var.name))

        # Reset domains as we're trying a different value
        for var_to_update in csp.vars:
            var_to_update.last[level + 1] = var_to_update.last[level]

    var.level = -1
    csp.assignments[varId] = None
    csp.nb_assigned -= 1

    return False
