from typing import Counter


def ac3(csp, level=0):
    """Removes all arc-inconsistent values for each variable of a csp

    Args:
        csp (CSP.CSP): A CSP solver

    Returns:

    """
    constrs = []
    for constr in csp.constrs:
        constrs.append(constr)
        constrs.append(constr.reverse())

    to_test = constrs[:]
    while to_test:

        c_xy = to_test.pop()
        x = c_xy.var1
        y = c_xy.var2

        values = x.dom(level)
        for a in values:

            supported = False
            for b in y.dom(level):
                if c_xy.is_feasible(a, b):
                    supported = True
                    break

            if not supported:
                x.remove_value(a, level)

                for c_zx in constrs:
                    if c_zx.var2 == x and c_zx.var1 != y:
                        if c_zx not in to_test:
                            to_test.append(c_zx)


def init_ac4(csp, level=0):
    Q = []
    Supporters = {(id, a) : list() for id in range(csp.nbVars) for a in csp.vars[id].dom(level)}
    Counters = {}

    for c in csp.constrs:
        x = c.var1
        y = c.var2
        values = x.dom(level)

        for a in values:
            total = 0
            for b in y.dom(level):
                if c.is_feasible(a, b):
                    total += 1
                    l = Supporters[(y.id, b)]
                    l.append((x.id, a))
                    Supporters.update({(y.id, b) : l})
            Counters.update({(x.id, y.id, a) : total})

            if Counters[(x.id, y.id, a)] == 0:
                x.remove_value(a, level)
                Q.append((x.id, a))
    
    return Q, Supporters, Counters


def ac4(csp, level=0):
    Q, Supporters, Counters = init_ac4(csp, level)

    while len(Q) >0 :
        element = Q.pop(0)
        y_id = element[0]
        for support in Supporters[element]:
            x_id = support[0]
            a = support[1]
            count = Counters[(x_id, y_id, a)]
            Counters.update({ (x_id, y_id, a) : count-1})

            if Counters[(x_id, y_id, a)] == 0 and a in csp.vars[x_id].dom(level) :
                csp.vars[x_id].remove_value(a, level)
                Q.append((x_id, a))

