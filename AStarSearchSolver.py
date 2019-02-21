#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 14:07:32 2019

@author: liaohaiguang
"""

import os
import operator
import numpy as np
import matplotlib.pyplot as plt

import Initializer as init
import GridGraph as graph
import TwoPinRouterASearch as twoPinASearch
import MST as tree



# The following function solve benchmarks with A* Search Algorithm 
# and return edge traffic information
def solve(benchmarkfile,solution_savepath):
    # Getting Net Info
    grid_info = init.read(benchmarkfile)
    gridParameters = init.gridParameters(grid_info)
    capacity = graph.GridGraph(init.gridParameters(grid_info)).generate_capacity()
    gridX,gridY,gridZ = graph.GridGraph(init.gridParameters(grid_info)).generate_grid()
    gridGraph = twoPinASearch.AStarSearchGraph(gridParameters, capacity)
    # Sort net
    halfWireLength = init.VisualGraph(init.gridParameters(grid_info)).bounding_length()
    sortedHalfWireLength = sorted(halfWireLength.items(),key=operator.itemgetter(1),reverse=True) # Large2Small
    routeListMerged = []
    routeListNotMerged = []
    for i in range(len(init.gridParameters(grid_info)['netInfo'])):
        print('*********************')
        print('Routing net No.',sortedHalfWireLength[i][0])
        netNum = int(sortedHalfWireLength[i][0])
        # # Remove pins that are in the same grid:
        netPinList = []
        netPinCoord = []
        for j in range(0, gridParameters['netInfo'][netNum]['numPins']):
            pin = tuple([int((gridParameters['netInfo'][netNum][str(j+1)][0]-gridParameters['Origin'][0])/gridParameters['tileWidth']),
                             int((gridParameters['netInfo'][netNum][str(j+1)][1]-gridParameters['Origin'][1])/gridParameters['tileHeight']),
                             int(gridParameters['netInfo'][netNum][str(j+1)][2]),
                              int(gridParameters['netInfo'][netNum][str(j+1)][0]),
                              int(gridParameters['netInfo'][netNum][str(j+1)][1])])
            if pin[0:3] in netPinCoord:
                continue
            else:
                netPinList.append(pin)
                netPinCoord.append(pin[0:3])
        twoPinList = []
        for i in range(len(netPinList)-1):
            pinStart = netPinList[i]
            pinEnd = netPinList[i+1]
            twoPinList.append([pinStart,pinEnd])
        # Insert Tree method to decompose two pin problems here
        twoPinList = tree.generateMST(twoPinList)
        # Remove pin pairs that are in the same grid again
        nullPairList = []
        for i in range(len(twoPinList)):
            if twoPinList[i][0][:3] == twoPinList[i][1][:3]:
                nullPairList.append(twoPinList[i])

        for i in range(len(nullPairList)):
            twoPinList.reomove(nullPairList[i])
        i = 1
        routeListSingleNet = []
        for twoPinPair in twoPinList:
            pinStart = twoPinPair[0]; pinEnd =  twoPinPair[1]
            route, cost = twoPinASearch.AStarSearchRouter(pinStart, pinEnd, gridGraph)
            routeListSingleNet.append(route)
            i += 1
#        print('Route List Single Net:',routeListSingleNet,'\n')
        mergedrouteListSingleNet = []
        for list in routeListSingleNet:
            for loc in list:
                    # if loc not in mergedrouteListSingleNet:
                    mergedrouteListSingleNet.append(loc)
#        print('Merged Route List Single Net',mergedrouteListSingleNet,'\n')
        routeListMerged.append(mergedrouteListSingleNet)
        routeListNotMerged.append(routeListSingleNet)
        # Update capacity and grid graph after routing one pin pair
        # # WARNING: capacity update could lead to failure since capacity could go to negative (possible bug)
        # # # print(route)
        capacity = graph.updateCapacity(capacity, mergedrouteListSingleNet)
        # gridGraph = twoPinASearch.AStarSearchGraph(gridParameters, capacity)
    print('\nRoute List Merged:',routeListMerged)
    
    # Visualize results
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_zlim(-0.5,2.5)
    #
    for routeList in routeListNotMerged:
        for route in routeList:
            x = [coord[3] for coord in route]
            y = [coord[4] for coord in route]
            z = [coord[2] for coord in route]
            ax.plot(x,y,z)

    plt.xlim([0, gridParameters['gridSize'][0]-1])
    plt.ylim([0, gridParameters['gridSize'][1]-1])
    plt.savefig('{path}RoutingVisualize_{benchmark}.jpg'.format(path=solution_savepath,\
                benchmark=benchmarkfile))
#    plt.show()
#    plt.close()
    
    f = open('{solution_savepath}{benchmark}Astar_solution'.format(\
                solution_savepath=solution_savepath,benchmark=benchmarkfile),'w+')
    for i in range(gridParameters['numNet']):
        indicator = i
        netNum = int(sortedHalfWireLength[i][0])
        i = netNum

        value = '{netName} {netID} {cost}\n'.format(netName=gridParameters['netInfo'][i]['netName'],
                                              netID = gridParameters['netInfo'][i]['netID'],
                                              cost = max(0,len(routeListMerged[indicator])-1))
        f.write(value)
        for j in range(len(routeListMerged[indicator])-1):
        # In generating the route in length coordinate system, the first pin (corresponding to griParameters['netInfo'][i]['1'])
        # is used as reference point
            a = routeListMerged[indicator][j]
            b = routeListMerged[indicator][j+1]
            diff = [abs(a[2]-b[2]),abs(a[3]-b[3]),abs(a[4]-b[4])]
            if diff[1] > 2 or diff[2] > 2:
                continue
            elif diff[1] == 2 or diff[2] == 2:
                # print('Alert')
                continue
            elif diff[0] == 0 and diff[1] == 0 and diff[2] == 0:
                continue
            elif diff[0] + diff[1] + diff[2] >= 2:
                continue
            else:
                value = '({},{},{})-({},{},{})\n'.format(a[0],a[1],a[2],b[0],b[1],b[2])
                f.write(value)
        f.write('!\n')
    f.close()
    return routeListMerged

if __name__ == "__main__":
    
    # get edge traffic (data structure: gridSize*gridSize*2)
#    edge_traffic =
    os.chdir("benchmark/")
    benchmarkfile = "test_benchmark_5.gr"
    
    
    solution_savepath = '../solutionsForBenchmark/' 
    os.mkdir(solution_savepath)

    solve(benchmarkfile,solution_savepath)
    
    
    
    
    
    
    
    
    
    