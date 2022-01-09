from Constraint import ConstraintBinary



def ac3(csp, level=-1):
    """Removes all arc-inconsistent values for each variable of a csp
    Args:
        csp (CSP.CSP): A CSP solver
        level (int): depth level at which arc-consistency is verified in a backtracking tree
    Returns:
        (bool): False if the problem is found unfeasible, True otherwise.
            True does not mean that the problem is feasible, just that unfeasibility was not proven yet
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

        dom_x = x.dom(level + 1)
        for a in dom_x:
            supported = False

            dom_y = y.dom(level + 1)
            for b in dom_y:
                if c_xy.is_feasible([a, b]):
                    supported = True
                    break

            if not supported:
                # print("ac3 remove {} of {} from {}".format(a, x.name, x.dom(level)))
                x.remove_value(a, level + 1)

                if x.current_dom_size[level + 1] == 0:
                    return False

                for c_zx in constrs:
                    if c_zx.var2.id == x.id and c_zx.var1.id != y.id:
                        if c_zx not in to_test:
                            to_test.append(c_zx)

    return True


def init_ac4(csp, level=-1):
    Q = []
    supporters = {(id, a): list() for id in range(csp.nbVars) for a in csp.vars[id].dom(level)}
    counters = {}

    constrs = []
    for constr in csp.constrs:
        if isinstance(constr, ConstraintBinary):
            constrs.append(constr)
            constrs.append(constr.reverse())

    contradiction = False
    for c in constrs:
        x = c.var1
        y = c.var2

        dom_x = x.dom(level + 1)
        for a in dom_x:
            total = 0

            dom_y = y.dom(level + 1)
            for b in dom_y:
                if c.is_feasible([a, b]):
                    total += 1
                    # l = supporters[(y.id, b)]
                    # l.append((x.id, a))
                    # supporters.update({(y.id, b): l})
                    supporters[(y.id, b)].append((x.id, a))

            counters.update({(x.id, y.id, a): total})

            if counters[(x.id, y.id, a)] == 0:
                x.remove_value(a, level + 1)
                Q.append((x.id, a))

                if x.current_dom_size[level + 1] == 0:
                    contradiction = True
                    break

        if contradiction:
            break
    
    return Q, supporters, counters, contradiction


def ac4(csp, level=-1):
    Q, supporters, counters, contradiction = init_ac4(csp, level)

    while len(Q) > 0 and not contradiction:
        element = Q.pop(0)
        y_id = element[0]
        for support in supporters[element]:
            x_id = support[0]
            a = support[1]

            counters[(x_id, y_id, a)] -= 1

            if counters[(x_id, y_id, a)] == 0:  # and a in csp.vars[x_id].dom(level + 1):
                csp.vars[x_id].remove_value(a, level + 1)
                Q.append((x_id, a))

                if csp.vars[x_id].current_dom_size[level + 1] == 0:
                    contradiction = True
                    break

    return not contradiction
