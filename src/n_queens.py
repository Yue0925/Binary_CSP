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
            if assignment[i] is None or assignment[j] is None: return False
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
    
    if isFeasible != verification(csp_solver.assignments):
        isFeasible = False
        print("The solution found by Solver is not valid ! ")
    return csp_solver.exploredNodes, csp_solver.exploreTime, isFeasible, csp_solver.timeOut


def benchmarking_consistency():
    import matplotlib.pyplot as plt

    instances = dict()  # algo (string) => instance size (list)
    usedTimes = dict()  # algo (string) => times (list)
    nodes = dict()  # algo (string) => nb nodes (list)

    for lookAhead in ["BT", "FC", "MAC3", "MAC4"]:
        for root in [None, "AC3", "AC4"]:

            if lookAhead == "MAC3" or lookAhead == "MAC4":
                if not root is None:
                    break
            
            method = lookAhead
            if not root is None:
                method += " + " + root
            sizes = []
            t = []
            n = []

            for N in [*list(range(5, 20)), *range(20, 50, 5)]:
                exploredNodes, exploreTime, isFeasible, timeOut = solve_nqueens(N, [lookAhead, root])
                if isFeasible:
                    sizes.append(N)
                    t.append(exploreTime)
                    n.append(exploredNodes)
                elif timeOut:
                    break
                else:
                    raise Exception("Solver cannot solve the {}-Queens problem".format(N))
            
            instances[method] = sizes
            usedTimes[method] = t
            nodes[method] = n


    # generate picture times
    for method in instances.keys():
        plt.plot(instances[method], usedTimes[method], label = method)

    plt.legend()
    plt.yscale("log")
    plt.xscale("log")
    plt.title("Comparison of computation times between look-ahead methods on N-Queens")
    plt.xlabel("Number of queens")
    plt.ylabel("Time(s)")
    plt.savefig('../results/N-Queens_impact_consistent_times.png')

    # generate picture nodes
    for method in instances.keys():
        plt.plot(instances[method], nodes[method], label = method)

    plt.title("Comparison of explored nodes between look-ahead methods on N-Queens")
    plt.xlabel("Number of queens")
    plt.ylabel("Number of nodes explored")
    plt.savefig('../results/N-Queens_impact_consistent_nodes.png')



def benchmarking_heuristics(selections: list, heurictics: str):
    import matplotlib.pyplot as plt

    select = dict()  # variable selection (string) => instance size (list)
    usedTimes = dict()  # variable selection (string) => times (list)
    nodes = dict()  # variable selection (string) => nb nodes (list)

    for option in range(len(selections)):
        
        method = selections[option]
        sizes = []
        t = []
        n = []

        for N in [*list(range(5, 20)), *range(20, 50, 5)]: 
            exploredNodes, exploreTime, isFeasible, timeOut = solve_nqueens(N, ["FC", "AC4"])
            if isFeasible:
                sizes.append(N)
                t.append(exploreTime)
                n.append(exploredNodes)
            elif timeOut:
                break
            else:
                raise Exception("Solver cannot solve the {}-Queens problem".format(N))
        
        select[method] = sizes
        usedTimes[method] = t
        nodes[method] = n


    # generate picture times
    for method in select.keys():
        plt.plot(select[method], usedTimes[method], label = method)

    plt.legend()
    plt.yscale("log")
    plt.xscale("log")
    plt.title("Comparison of computation times between {} order heuristics on N-Queens".format(heurictics))
    plt.xlabel("Number of queens")
    plt.ylabel("Time(s)")
    plt.savefig('../results/N-Queens_{}_heuristics_times.png'.format(heurictics))

    # generate picture nodes
    for method in select.keys():
        plt.plot(select[method], nodes[method], label = method)

    plt.title("Comparison of explored nodes between variables order heuristics on N-Queens")
    plt.xlabel("Number of queens")
    plt.ylabel("Number of nodes explored")
    plt.savefig('../results/N-Queens_{}_heuristics_nodes.png'.format(heurictics))


if __name__ == "__main__":
    # import timeit
    # print(timeit.timeit("solve_nqueens(10)", globals=locals()))

    #solve_nqueens(15, settings=["MAC4"])
    benchmarking_consistency()

    for (s, h) in [(VARIABLES_SELECTION, "variables"), (VALUES_SELECTION, "values")]:
        benchmarking_heuristics(s, h)
