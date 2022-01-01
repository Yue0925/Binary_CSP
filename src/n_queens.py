#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from CSP import *

def constr_nqueens(x: int, y: int, a: int, b: int):
    return (a != b) and (abs(x - y) != abs(a - b))


def display_sol_nqueens(csp: CSP, N: int):
    """ Display the solution information of n-Queens problem solved by CSP solver. """

    print("\n \nSolution of {}-Queens problem : ".format(N))
    for i in range(N):
        for j in range(1, N + 1):
            if csp.assignments[i] == j: 
                print('Q ', end='')
            else:
                print('. ', end='')
        print()
    
    print("\n\nCSP solver explored {} nodes in the research tree.".format(csp.exploredNodes))
    print("Total {}s used in the tree exploration.".format(csp.exploreTime))
    print("Sol is feasible ? {}".format(csp.isFeasible))
    


def solve_nqueens(N: int):
    # modelization
    csp_solver = CSP()

    # N variables, (i, xi) position of each queen
    for i in range(N):
        csp_solver.add_variable("x{}".format(i+1), 1, N)
    
    # constraints, for every two distinct queens
    for i in range(N-1):
        for j in range(i+1, N):
            csp_solver.add_constraint_enum(i, j, constr_nqueens)
    
    csp_solver.display()

    csp_solver.set_variable_selection(0)
    csp_solver.set_value_selection(3)

    csp_solver.solve()
    display_sol_nqueens(csp_solver, N)


if __name__ == "__main__":

    print(" test n queens ! ")

    solve_nqueens(10)

