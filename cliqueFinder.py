import sys, getopt
from itertools import permutations
from collections import defaultdict
from pysmt.shortcuts import Symbol, Equals, Plus, Min, Max, And, Int, GT, GE, LE, LT, Or, Not, is_sat, Solver, get_model
from pysmt.typing import INT
from igraph import *
import numpy as np
import time


def printUsage():
    print("USAGE: %s <graph.csv file> -m" % sys.argv[0])
    print("Options:")
    print("-m get max-cliques")
    print("-k get k-cliques")
    print("-n limit output to n number of cliques")


def generateSatFormula_old(G,k):
    V = [x for x in G.keys()]
    VSymb = [Symbol(x) for x in V]
    possibleCliques = list(permutations(VSymb, r=k))
    cliqueConstraints = [And(x) for x in possibleCliques]
    edgeConstraints = []
    for i in range(0,len(V)):
        v1 = V[i]
        for j in range(i+1,len(V)):
            v2 = V[j]
            if not(G[v1][v2]):
                f = Or(Not(Symbol(v1)),Not(Symbol(v2)))
                edgeConstraints.append(f)
    sat = And(And(edgeConstraints),Or(cliqueConstraints))
    return sat

def generateSatFormula(G,k):
    domains = []
    edgeConstraints = []
    V = [x for x in G.keys()]
    symb = [Symbol(v + "_int", INT) for v in V]
    domains.append(Equals(Plus(symb),Int(k)))
    for v in V:
        domains.append(LE(Symbol(v + "_int", INT),Int(1)))
        domains.append(GE(Symbol(v + "_int", INT),Int(0)))
        edgeConstraints.append(Or(Equals(Symbol(v + "_int", INT),Int(0)), Symbol(v)))
        edgeConstraints.append(Or(Equals(Symbol(v + "_int", INT),Int(1)), Not(Symbol(v))))
    for i in range(0,len(V)):
        v1 = V[i]
        for j in range(i+1,len(V)):
            v2 = V[j]
            if not(G[v1][v2]):
                f = Or(Not(Symbol(v1)),Not(Symbol(v2)))
                edgeConstraints.append(f)
    sat = And(And(domains),And(edgeConstraints))
    return sat

def generateSatFormulaRange(G,kMin,kMax):
    domains = []
    edgeConstraints = []
    V = [x for x in G.keys()]
    symb = [Symbol(v + "_int", INT) for v in V]
    domains.append(GE(Plus(symb),Int(kMin)))
    domains.append(LE(Plus(symb),Int(kMax)))
    for v in V:
        domains.append(LE(Symbol(v + "_int", INT),Int(1)))
        domains.append(GE(Symbol(v + "_int", INT),Int(0)))
        edgeConstraints.append(Or(Equals(Symbol(v + "_int", INT),Int(0)), Symbol(v)))
        edgeConstraints.append(Or(Equals(Symbol(v + "_int", INT),Int(1)), Not(Symbol(v))))
    for i in range(0,len(V)):
        v1 = V[i]
        for j in range(i+1,len(V)):
            v2 = V[j]
            if not(G[v1][v2]):
                f = Or(Not(Symbol(v1)),Not(Symbol(v2)))
                edgeConstraints.append(f)
    sat = And(And(domains),And(edgeConstraints))
    return sat


def negateSolutionInFormula(sat,solution):
    negSolution = Or([Not(Symbol(x)) for x in solution])
    newSat = And(sat,negSolution)
    return newSat

def getAllSolutions(G,sat,maxSolutions=float("inf")):
    solutions = []
    satCpy = sat
    while True:
        solution = getSolution(G,satCpy)
        if solution == None:
            break
        else:
            solutions.append(solution);
            if len(solutions) >= maxSolutions:
                break
            satCpy = negateSolutionInFormula(satCpy,solution)
    return solutions    
    
def loadGraph(inputFile):
    G = defaultdict(lambda: defaultdict(int))
    f = open(inputFile,"r")
    for line in f.readlines():
        v1,v2 = line.rstrip().split(",");
        v1 = "v_" + v1
        v2 = "v_" + v2
        G[str(v1)][str(v2)] = 1;
        G[str(v2)][str(v1)] = 1;
    f.close()
    return G;

def completeTestGraph(k):
    G = defaultdict(lambda: defaultdict(int))
    for i in range(1,k+1):
        for j in range(i,k+1):
            G["x" + str(i)]["x" + str(j)] = 1;
            G["x" + str(j)]["x" + str(i)] = 1;            
    return G

def getRandomGraph(graphSize,prob=0.1):
    G = defaultdict(lambda: defaultdict(int))
    for i in range(1,graphSize+1):
        for j in range(i+1,graphSize+1):
            if np.random.choice([0,1],1,p=[1-prob,prob])[0]:
                G["x" + str(i)]["x" + str(j)] = 1;
                G["x" + str(j)]["x" + str(i)] = 1;            
    return G

def getSolution(G,sat):
    solution = []
    modelResults = {}
    V = [x for x in G.keys()]
    model = get_model(sat)
    if model == None:
        return None
    for k in V:
        if str(model[Symbol(k)]) == "True":
            solution.append(k)
    return solution

def getMaxSat(G):
    kMin = 2
    kMax = len(G.keys())
    #print("trying %d ... %d" % (kMin,kMax))
    sat = generateSatFormulaRange(G,kMin,kMax)
    solution = getSolution(G,sat)
    if solution == None:
        return 0, None
    else:
        kMin = len(solution)
        #print kMin
    #print solution
    while kMin != kMax:
        m = kMin + (kMax - kMin) / 2 + 1
        #print("kMin=%d..kMax=%d (m=%d)\n" % (kMin,kMax,m))
        if m <= kMax:
            #print("trying %d ... %d" % (m,kMax))
            sat = generateSatFormulaRange(G,m,kMax)
            solution = getSolution(G,sat)
            if solution == None:
                #print "None"
                kMax = m - 1
            else:
                kMin = len(solution)
    sat = generateSatFormula(G,kMin)
    solution = getSolution(G,sat)
    return kMin,solution

            

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        printUsage();
        exit()
    try:
        opts, args = getopt.getopt(sys.argv[2:], "mk:n:", [])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
    optArgs = {}
    for o, a in opts:
        optArgs[o] = a

    G = loadGraph(sys.argv[1])
    if "-m" in optArgs and "-k" in optArgs:
        print "-m and -k options cannot be used toghether\n"
        printUsage()
        exit(1)
    elif "-m" in optArgs:
        k, sat = getMaxSat(G)
        if "-n" in optArgs:
            sat = generateSatFormula(G,k=k)
            solutions = getAllSolutions(G,sat,maxSolutions=int(optArgs["-n"]))
            print solutions
        else:
            sat = generateSatFormula(G,k=k)
            solutions = getAllSolutions(G,sat)
            print solutions
    elif "-k" in optArgs:
        sat = generateSatFormula(G,k=int(optArgs["-k"]))
        if "-n" in optArgs:
            solutions = getAllSolutions(G,sat,maxSolutions=int(optArgs["-n"]))
            print solutions
        else:
            solutions = getAllSolutions(G,sat)
            print solutions
    elif len(optArgs) == 0:
        printUsage()
        exit();
        

