#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from CSP import *

def domFun():
    pass



if __name__ == "__main__":
    print(" test.py ! ")
    var1 = Variable(
        0,
        "var1",
        0,
        1
    )
    var2 = Variable(
        1,
        "var2",
        0,
        1
    )

    const1 = Constraint(var1, var2)
    myCSP = CSP(2, [var1, var2], 1, const1)

    print(const1)
    for (a, b) in const1.feasibleTuples:
        print("(", a, ", ", b, ")")
    