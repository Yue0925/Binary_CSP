def ac3(csp):
    constrs = []
    for constr in csp.constrs:
        constrs.append(constr)
        constrs.append(constr.reverse())

    to_test = constrs[:]
    while to_test:

        c_xy = to_test.pop()
        x = c_xy.var1
        y = c_xy.var2

        values = x.domEnum.copy()
        for a in values:

            supported = False
            for b in y.domEnum:
                if c_xy.is_feasible(a, b):
                    supported = True
                    break

            if not supported:
                x.domEnum.remove(a)

                for c_zx in constrs:
                    if c_zx.var2 == x and c_zx.var1 != y:
                        if c_zx not in to_test:
                            to_test.append(c_zx)
