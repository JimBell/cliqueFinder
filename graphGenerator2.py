#!/usr/bin/python
import sys, getopt
from itertools import permutations
from collections import defaultdict
import numpy as np
import time
import random


def createInitialConnections(G,vOrder,numVert):
    #constructs a random set of trees off of the clique
    for i in range(0,numVert):
        if i not in vOrder:
            r = random.randint(0,numVert-1)
            if r == i and (r / float(numVert)) > 0.5:
                r = r - 1
            elif r == i:
                r = r + 1
            #test    
            if i == r:
                print "error i equals r"
            ####
            G[i][r] = 1
            G[r][i] = 1
            vOrder[i] += 1
            vOrder[r] += 1
            #print "add1"

def getNextEdge(G,eNoAdd,numVert):
    V = G.keys()
    cantAddCount = 0
    iStart = random.randint(0,numVert-1)
    v1 = V[iStart]
    while cantAddCount < numVert:
        if len(eNoAdd[v1].keys()) == numVert:
            cantAddCount += 1
            iStart = (iStart + 1) % numVert
            v1 = V[iStart]
        else:
            break
    if cantAddCount >= numVert:
        return 0,0,True
    jStart = random.randint(0,numVert-1)
    v2 = V[jStart]
    while True:
        if eNoAdd[v1][v2] == 1:
            jStart = (jStart + 1) % numVert
            v2 = V[jStart]
        else:
            break
    return v1,v2,False

def canAdd(G,v1,v2,maxClique):
    maxMatching = maxClique - 3
    count = 0
    if G[v1][v2] == 1:
        print("error: %d and %d edge already added" % (v1,v2))
        exit()
    for k in G[v1].keys():
            if G[v1][k] == 1 and G[v2][k] == 1:
                count += 1
                if count > maxMatching:
                    return False
    return True
    

def addAdditionalConnections(G,vOrder,numVert,numEdges,maxClique):
    eCount = 0
    eNoAdd = defaultdict(lambda: defaultdict(int))
    for v1 in G.keys():
        eNoAdd[v1][v1] = 1
        for v2 in G.keys():
            if G[v1][v2]:
                eCount += 1
                eNoAdd[v1][v2] = 1
    eCount = eCount / 2

    V = G.keys()
    while eCount < numEdges:
        v1,v2,done = getNextEdge(G,eNoAdd,numVert)
        if done:
            break
        else:
            if canAdd(G,v1,v2,maxClique):
                G[v1][v2] = 1
                G[v2][v1] = 1
                eCount += 1
            eNoAdd[v1][v2] = 1
            eNoAdd[v2][v1] = 1
        
def generateClique(G,vOrder,numVert,maxClique):
    cliqueNodes = {}
    perm = np.random.permutation(numVert)
    for i in range(0,maxClique):
        cliqueNodes[perm[i]] = 1
    for v1 in cliqueNodes.keys():
        for v2 in cliqueNodes.keys():
            if v1 != v2:
                G[v1][v2] = 1
                G[v2][v1] = 1
    for v1 in cliqueNodes.keys():
        vOrder[v1] = len(G[v1].keys())
    

def generateGraph(numVert,numEdges,maxClique):
    #print numVert,numEdges,maxClique
    vOrder = defaultdict(int)
    G = defaultdict(lambda: defaultdict(int))
    generateClique(G,vOrder,numVert,maxClique)
    createInitialConnections(G,vOrder,numVert)
    #addAdditionalConnections(G,vOrder,numVert,numEdges,maxClique)
    return G

def getGraphStats(G):
    V = G.keys()
    vCount = len(V)
    eCount = 0
    for i in range(0,len(V)):
        for j in range(i+1,len(V)):
            v1,v2 = V[i],V[j]
            if G[v1][v2] > 0:
                eCount += 1
    return vCount,eCount
            
def printGraphToFile(G,maxClique,outputPrefix):
    vCount,eCount = getGraphStats(G)
    outputFile = outputPrefix + "_v" + str(vCount) + "_e" + str(eCount) + "_maxk" + str(maxClique) + ".txt"
    print("%d\t%d\t%d\t%s" % (vCount,eCount,maxClique,outputFile))
    f = open(outputFile,"w")
    V = G.keys()
    for i in range(0,len(V)):
        for j in range(i+1,len(V)):
            v1,v2 = V[i],V[j]
            if G[v1][v2] > 0:
                f.write("%d,%d\n" % (v1,v2))
    f.close()

def getNextDroppableEdge(G,eNoDrop,numVert):
    V = G.keys()
    cantDropCount = 0
    iStart = random.randint(0,numVert-1)
    v1 = V[iStart]
    while cantDropCount < numVert:
        if len(eNoDrop[v1].keys()) == numVert:
            cantDropCount += 1
            iStart = (iStart + 1) % numVert
            v1 = V[iStart]
        else:
            break
    if cantDropCount >= numVert:
        return 0,0,True
    jStart = random.randint(0,numVert-1)
    v2 = V[jStart]
    while True:
        if eNoDrop[v1][v2] == 1:
            jStart = (jStart + 1) % numVert
            v2 = V[jStart]
        else:
            break
    return v1,v2,False

def dropEdges(G,numEdges,maxClique):
    vCount,eCount = getGraphStats(G)
    eNoDrop = defaultdict(lambda: defaultdict(int))
    for i in range(0,maxClique):
        for j in range(0,maxClique):
            eNoDrop[i][j] = 1
    for v1 in G.keys():
        eNoDrop[v1][v1] = 1
        for v2 in G.keys():
            if G[v1][v2] == 0:
                eNoDrop[v1][v2] = 1
    #print("eCount=",eCount,",numEdges=",numEdges)
    while eCount > numEdges:
        v1,v2,done = getNextDroppableEdge(G,eNoDrop,numVert)
        if done:
            break
        else:
            v1Order = len([k for k in G[v1].keys() if G[v1][k] > 0])
            v2Order = len([k for k in G[v2].keys() if G[v2][k] > 0])
            if v1Order > 1 and v2Order > 1:
                G[v1][v2] = 0
                G[v2][v1] = 0
                eCount -= 1
                #print("dropping",v1,v2)
        eNoDrop[v1][v2] = 1
        eNoDrop[v2][v1] = 1

def genSubCliqeGraph(G,numVert,maxClique):
    k = maxClique - 1
    subClique = []
    for i in range(0,k):
        subClique.append(i)
    for i in subClique:
        for j in subClique:
            G[i][j] = 1
            G[j][i] = 1
    #print subClique
    for n in range(k,numVert):
        z = random.randint(0,k-1)
        subClique.pop(z)
        subClique.append(n)
        #print subClique
        for i in subClique:
            for j in subClique:
                G[i][j] = 1
                G[j][i] = 1    

def genGraph2(numVert,numEdges,maxClique):
    #print numVert,numEdges,maxClique
    vOrder = defaultdict(int)
    G = defaultdict(lambda: defaultdict(int))
    generateClique(G,vOrder,numVert,maxClique)
    genSubCliqeGraph(G,numVert,maxClique)
    dropEdges(G,numEdges,maxClique)
    return G


if __name__ == "__main__":
    if (len(sys.argv) < 4):
        print("USAGE: %s <num nodes> <num edges> <max clique size>" % sys.argv[0])
        exit()

    numVert = int(sys.argv[1])
    numEdges = int(sys.argv[2])
    maxClique = int(sys.argv[3])

    #print numVert,numEdges,maxClique
    #G = generateGraph(numVert,numEdges,maxClique)

    G = generateGraph(numVert,numEdges,maxClique)
    vCount,eCount = getGraphStats(G)
    printGraphToFile(G,maxClique,"graph")
    #outputPrefix + "_v" + str(vCount) + "_e" + str(eCount) + "_maxk" + str(maxClique) + ".txt"
    #print("%d\t%d\t%d\t%s" % (vCount,eCount,maxClique,outputFile))

    #printGraphToFile(G,maxClique,"graph")
    
    #vCount,eCount = getGraphStats(G)
    #print("vCount=%d, eCount=%d\n" % (vCount,eCount))
    #if (numEdges == eCount):
    #    printGraphToFile(G,maxClique,"graph")
    #else:
    #    #print("Error: can't get right number of edges.  edges = %d vs %d\n" % (eCount,numEdges));
