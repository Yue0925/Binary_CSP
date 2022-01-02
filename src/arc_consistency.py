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


