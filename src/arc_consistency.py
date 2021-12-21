def ac3(csp):
    to_test = csp.constraints

    while to_test:
        c_xy = to_test.pop()
        x, y = c_xy.variables

        for a in x.domain:
            for b in y.domain:

                if not c_xy(a, b):
                    x.remove(a)

                    for c_zx in csp.constraints:
                        if c_zx.variables[1] == x and c_zx.variables[0] != y:
                            if c_zx not in to_test:
                                to_test.append(c_zx)
