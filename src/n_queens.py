#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from CSP import *


def constr_nqueens(x: int, y: int, a: int, b: int):
    return abs(x - y) != abs(a - b)

def verification(assignment: list) -> bool:
    """ Verify if the given solution is satisfied by N-Queens problem. """
    N = len(assignment)
    for i in range(N-1):
        for j in range(i+1, N):
            if not constr_nqueens(i, j, assignment[i], assignment[j]):
                return False
    return True

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
    

def solve_nqueens(N: int, settings=None):
    # modelization
    csp_solver = CSP()

    # N variables, (i, xi) position of each queen
    x = []
    for i in range(N):
        x.append(csp_solver.add_variable("x{}".format(i+1), 1, N))
    
    # constraints, for every two distinct queens
    for i in range(N-1):
        for j in range(i+1, N):
            csp_solver.add_constraint_enum(i, j, constr_nqueens)
            # csp_solver.add_constraint(x[i] - x[j] != j - i)  # Using 2 constraints is slightly less efficient
            # csp_solver.add_constraint(x[j] - x[i] != j - i)
    csp_solver.add_all_diff(x)

    # parameters settings
    # by default, we use the backtracking algorithm
    if settings is None:
        csp_solver.set_BT()
    else:
        for param in settings:
            if param == "BT":
                csp_solver.set_BT()
            if param == "FC":
                csp_solver.set_FC()
            if param == "MAC3":
                csp_solver.set_MAC3()
            if param == "MAC4":
                csp_solver.set_MAC4()
            if param == "AC3":
                csp_solver.set_AC3()
            if param == "AC4":
                csp_solver.set_AC4()

    csp_solver.set_variable_selection(3)
    csp_solver.set_value_selection(3)

    isFeasible = csp_solver.solve()
    display_sol_nqueens(csp_solver, N)
    return csp_solver.exploredNodes, csp_solver.exploreTime, isFeasible


def benchmarking():
    import matplotlib.pyplot as plt

    instances = dict()  # algo (string) => instance size (list)
    usedTimes = dict()  # algo (string) => times (list)
    nodes = dict()  # algo (string) => nb nodes (list)

    for compo1 in ["BT", "FC"]:
        for compo2 in [None, "MAC3", "MAC4", "AC3", "AC4"]:
            method = compo1
            if compo2 is not None:
                method += " + " + compo2
            sizes = []
            t = []
            n = []

            for N in [*list(range(5, 15, 5)), *range(10, 50, 500)]:  # TODO : a corriger
                exploredNodes, exploreTime, isFeasible = solve_nqueens(N, [compo1, compo2])
                if isFeasible:
                    sizes.append(N)
                    t.append(exploreTime)
                    n.append(exploredNodes)
               
            instances[method] = sizes
            usedTimes[method] = t
            nodes[method] = n
    
    # generate picture times
    for method in instances.keys():
        plt.plot(instances[method], usedTimes[method], label = method)

    plt.legend()
    plt.title("Comparison of computation times between look-ahead methods on N-Queens")
    plt.xlabel("Number of queens")
    plt.ylabel("Time(s)")
    plt.savefig('../results/N-Queens_benchmarking_times.png')

    # generate picture nodes
    for method in instances.keys():
        plt.plot(instances[method], nodes[method], label = method)

    plt.legend()
    plt.title("Comparison of explored nodes between look-ahead methods on N-Queens")
    plt.xlabel("Number of queens")
    plt.ylabel("Number of nodes explored")
    plt.savefig('../results/N-Queens_benchmarking_nodes.png')


if __name__ == "__main__":
    # import timeit
    # print(timeit.timeit("solve_nqueens(10)", globals=locals()))

    # solve_nqueens(23, settings=["FC"])
    benchmarking()
