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
    #csp_solver.set_AC3()
    #csp_solver.set_BT()
    csp_solver.set_AC4()
    csp_solver.set_FC()

    csp_solver.set_variable_selection(3)
    csp_solver.set_value_selection(3)

    # solve
    isFeasible = csp_solver.solve()

    print("\n\nCSP solver explored {} nodes in the research tree.".format(csp_solver.exploredNodes))
    print("Total {}s used in the tree exploration.".format(csp_solver.exploreTime))
    print("Sol is feasible ? {}".format(csp_solver.isFeasible))

    return nodes, edges, isFeasible, csp_solver.exploredNodes, csp_solver.exploreTime




if __name__ == "__main__":
    chromaticsKnown = { "myciel3.col": 4, "myciel4.col": 5, "myciel5.col": 6, "myciel6.col": 7, "myciel7.col": 8,
        "anna.col" : 11, "david.col": 11, "homer.col": 13, "le450_15b.col": 15, "huck.col": 11, "jean.col": 10,
        "games120.col" : 9, "miles250.col": 8, "queen7_7.col": 7, "queen11_11.col": 11, "miles500.col": 20,
        "le450_25a.col": 25, "le450_5a.col": 5, "mulsol.i.1.col": 49, "zeroin.i.1.col": 49, "zeroin.i.2.col": 30, 
        "miles1000.col": 42}

    directory = "../instances/"

    with open('../results/Coloring.tex', 'w') as f:
        latex = r"""\documentclass{article}

\usepackage[french]{babel}
\usepackage [utf8] {inputenc} % utf-8 / latin1
\usepackage{multicol}

\setlength{\hoffset}{-18pt}
\setlength{\oddsidemargin}{0pt} % Marge gauche sur pages impaires
\setlength{\evensidemargin}{9pt} % Marge gauche sur pages paires
\setlength{\marginparwidth}{54pt} % Largeur de note dans la marge
\setlength{\textwidth}{481pt} % Largeur de la zone de texte (17cm)
\setlength{\voffset}{-18pt} % Bon pour DOS
\setlength{\marginparsep}{7pt} % Séparation de la marge
\setlength{\topmargin}{0pt} % Pas de marge en haut
\setlength{\headheight}{13pt} % Haut de page
\setlength{\headsep}{10pt} % Entre le haut de page et le texte
\setlength{\footskip}{27pt} % Bas de page + séparation
\setlength{\textheight}{668pt} % Hauteur de la zone de texte (25cm)

\begin{document}
\begin{center}
\renewcommand{\arraystretch}{1.4}
 \begin{tabular}{lccccc}
	\hline
\textbf{Instance}  & \textbf{vertices} & \textbf{edges}  & \textbf{Chromatic Number} & \textbf{Time(s)} & \textbf{Explored Nodes} \\\hline

"""
        f.write(latex)

        for instance in chromaticsKnown.items():
            nodes, edges, isFeasible, exploredNodes, exploreTime = solve_coloring(directory + instance[0], instance[1])
            f.write("{} & {} & {} & ".format(instance[0], nodes, edges))
            if isFeasible:
                f.write("{} & ".format(instance[1]))
            else:
                f.write("- & ")
            f.write("{} & {} \\\\ \n".format(exploreTime, exploredNodes))
        
        latex = r"""
\\
\hline\end{tabular}
\end{center}


\end{document}"""
        f.write(latex)

    

