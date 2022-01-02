#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import numpy as np
from CSP import *
# from backtrack import *
from arc_consistency import ac3

seed = 7
# random.seed(seed)
# np.random.seed(seed)


def constrFun1(x1, x2, v1:int, v2 : int):
    return v1 != v2


if __name__ == "__main__":
    print(" test.py ! ")
 
    # test 2-coloration with C_4
    print("\n\n\n 2-Coloration on C_4 \n\n")
    csp_solver = CSP()
    csp_solver.add_variable("x11", 1, 2)
    csp_solver.add_variable("x12", 1, 2)
    csp_solver.add_variable("x21", 1, 2)
    csp_solver.add_variable("x22", 1, 2)

    # csp_solver.add_constraint_enum(0, 1, constrFun1) #x11 != x12
    # csp_solver.add_constraint_enum(0, 2, constrFun1) #x11 != x21
    # csp_solver.add_constraint_enum(3, 1, constrFun1) # x22 != x12
    # csp_solver.add_constraint_enum(3, 2, constrFun1) # x22 != x21
    csp_solver.add_constraint(csp_solver.vars[0] != csp_solver.vars[1])
    csp_solver.add_constraint(csp_solver.vars[0] != csp_solver.vars[2])
    csp_solver.add_constraint(csp_solver.vars[3] != csp_solver.vars[1])
    csp_solver.add_constraint(csp_solver.vars[3] != csp_solver.vars[2])

    csp_solver.display()

    csp_solver.set_AC3()
    #csp_solver.set_BT()
    csp_solver.set_FC()

    csp_solver.set_variable_selection(0)
    csp_solver.set_value_selection(3)


    iter = 0
    while iter < 1 and csp_solver.solve():
        print()
        print()
        iter += 1
