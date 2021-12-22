#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from CSP import *
# from backtrack import *
from arc_consistency import ac3




def constrFun1(v1:int, v2 : int):
    return v1 != v2


if __name__ == "__main__":
    print(" test.py ! ")
    """
    myCSP = CSP()

    myCSP.add_variable(
        "var1",
        0,
        1)

    myCSP.add_variable(
        "var2",
        0,
        1
    )

    myCSP.add_constraint(0, 1)

    myCSP.display()
    """
    


    # test 2-coloration with C_4
    print("\n\n\n 2-Coloration on C_4 \n\n")
    csp_solver = CSP()
    csp_solver.add_variable("x11", 2, 2)
    csp_solver.add_variable("x12", 1, 2)
    csp_solver.add_variable("x21", 1, 2)
    csp_solver.add_variable("x22", 1, 2)

    csp_solver.add_constraint(0, 1, constrFun1) #x11 != x12
    csp_solver.add_constraint(0, 2, constrFun1) #x11 != x21
    csp_solver.add_constraint(3, 1, constrFun1) # x22 != x12
    csp_solver.add_constraint(3, 2, constrFun1) # x22 != x21

    csp_solver.display()

    # print("before AC3")
    # for var in csp_solver.vars:
    #     print(var.name, var.dom)
    #
    # ac3(csp_solver)
    #
    # print("After AC3")
    # for var in csp_solver.vars:
    #     print(var.name, var.dom)

    csp_solver.solve()
