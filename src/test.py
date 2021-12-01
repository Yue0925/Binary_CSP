#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from CSP import *

if __name__ == "__main__":
    print(" here ! ")
    var1 = Variable(
        0,
        "var1",
        0,
        1,
        set()
    )
    var2 = Variable(
        1,
        "var2",
        0,
        1,
        set()
    )

    const1 = Constraint(var1, var2, set())
    myCSP = CSP(2, [var1, var2], 1, const1)