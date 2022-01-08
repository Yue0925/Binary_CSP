from Constraint import ConstraintBinary



def ac3(csp, level=0):
    """Removes all arc-inconsistent values for each variable of a csp
    Args:
        csp (CSP.CSP): A CSP solver
        level (int): depth level at which arc-consistency is verified in a backtracking tree
    Returns:
    """
    constrs = []
    for constr in csp.constrs:
        if isinstance(constr, ConstraintBinary):  # Does not check all diff constraints for simplicity
            constrs.append(constr)
            constrs.append(constr.reverse())

    to_test = constrs[:]
    while to_test:

        c_xy = to_test.pop()
        x = c_xy.var1
        y = c_xy.var2

        if csp.assignments[x.id] is None:
            values = x.dom(level)
        else: values = [csp.assignments[x.id]]

        for a in values:
            supported = False

            if csp.assignments[y.id] is None:
                valuesB = y.dom(level)
            else: valuesB = [csp.assignments[y.id]]

            for b in valuesB:
                if c_xy.is_feasible([a, b]):
                    supported = True
                    break

            if not supported:
                # print("ac3 remove {} of {} from {}".format(a, x.name, x.dom(level)))
                x.remove_value(a, level)

                for c_zx in constrs:
                    if c_zx.var2.id == x.id and c_zx.var1.id != y.id:
                        if c_zx not in to_test:
                            to_test.append(c_zx)


def init_ac4(csp, level=0):
    Q = []
    supporters = {(id, a): list() for id in range(csp.nbVars) for a in csp.vars[id].dom(level)}
    counters = {}

    constrs = []
    for constr in csp.constrs:
        if isinstance(constr, ConstraintBinary):
            constrs.append(constr)
            constrs.append(constr.reverse())

    for c in constrs:
        if not isinstance(c, ConstraintBinary):
            continue
        x = c.var1
        y = c.var2
        if csp.assignments[x.id] is None:
            values = x.dom(level)
        else: values = [csp.assignments[x.id]]

        for a in values:
            total = 0
            if csp.assignments[y.id] is None:
                valuesB = y.dom(level)
            else: valuesB = [csp.assignments[y.id]]

            for b in valuesB:
                if c.is_feasible([a, b]):
                    total += 1
                    l = supporters[(y.id, b)]
                    l.append((x.id, a))
                    supporters.update({(y.id, b) : l})
            counters.update({(x.id, y.id, a) : total})

            if counters[(x.id, y.id, a)] == 0:
                x.remove_value(a, level)
                Q.append((x.id, a))
    
    return Q, supporters, counters


def ac4(csp, level=0):
    Q, supporters, counters = init_ac4(csp, level)
    while len(Q) > 0:
        element = Q.pop(0)
        y_id = element[0]
        for support in supporters[element]:
            x_id = support[0]
            a = support[1]
            count = counters[(x_id, y_id, a)]
            counters.update({(x_id, y_id, a): count-1})

            if counters[(x_id, y_id, a)] == 0 and a in csp.vars[x_id].dom(level):
                csp.vars[x_id].remove_value(a, level)
                Q.append((x_id, a))