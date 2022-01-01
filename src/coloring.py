#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from CSP import *
import os


def constr_coloring(x: int, y: int, a: int, b: int):
    return a != b

def lecture(path: str):
    if not os.path.exists(path): raise Exception("The input file {} doesn't exisist !".format(path))
    print("Reading file {}".format(path))
    matrixIncidency = None 
    edges = 0

    with open(path, 'r') as file:
        for line in file.readlines():
            if line[0] == 'c': # comments
                continue
            if line[0] == 'p': # graph size
                nodes = int(line.split()[2])
                matrixIncidency = [[False for _ in range(nodes)] for _ in range(nodes)] 
            if line[0] == 'e' : # we only consider the simple undirected graph
                u = int(line.split()[1])-1
                v = int(line.split()[2])-1
                if not matrixIncidency[u][v]:
                    matrixIncidency[u][v] = True
                    matrixIncidency[v][u] = True
                    edges += 1
    print("Graph has {} nodes and {} edges .".format(len(matrixIncidency), edges))
    return matrixIncidency, nodes, edges


def solve_coloring(path: str, upperB=0):
    """ Solve the (simple undirected) graph coloring problem with a defaut given chromatic number. """
    matrix, nodes, edges = lecture(path)

    if upperB==0:
        upperB = max(list(map(sum, matrix))) + 1 # set upper bound as the maximum degree + 1

    # modelization
    csp_solver = CSP()

    # variables
    for i in range(nodes):
        csp_solver.add_variable("x{}".format(i), 1, upperB)

    # constraints
    for u in range(nodes-1):
        for v in range(u+1, nodes):
            if matrix[u][v]: # if u, v are adjacent
                csp_solver.add_constraint_enum(u, v, constr_coloring)

    # parameters setting
    csp_solver.set_variable_selection(0)
    csp_solver.set_value_selection(3)

    # solve
    csp_solver.solve()

    print("\n\nCSP solver explored {} nodes in the research tree.".format(csp_solver.exploredNodes))
    print("Total {}s used in the tree exploration.".format(csp_solver.exploreTime))
    print("Sol is feasible ? {}".format(csp_solver.isFeasible))



if __name__ == "__main__":
    path = "../instances/anna.col"
    solve_coloring(path, 11)