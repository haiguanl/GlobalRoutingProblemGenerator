#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 10:14:16 2019

@author: liaohaiguang
"""

import numpy as np
import os
import argparse
import matplotlib.pyplot as plt

import AStarSearchSolver as solver

# Input parameters:
# Default setting: minWidth = 1, minSpacing = 0, 
# tileLength = 10, tileHeight = 10

# 1. Grid Size: for 8-by-8 benchmark, grid size is 8
# 2. vCap and hCap represents vertical capacity for layer2,
# and horizontal capacity for layer 1; unspecified capacity are 
# by default 0
# 3. maxPinNum: maximum number of pins of one net
# 4. capReduce: number of capacity reduction specification, by default = 0

def generator(benchmark_name,gridSize,netNum,vCap,hCap,maxPinNum,savepath,capReduce=0):
    
    file = open('%s' % benchmark_name, 'w+')
    
    # Write general information
    file.write('grid {gridSize} {gridSize} 2\n'.format(gridSize=gridSize))
    file.write('vertical capacity 0 {vCap}\n'.format(vCap=vCap))
    file.write('horizontal capacity {hCap} 0\n'.format(hCap=hCap))
    file.write('minimum width 1 1\n')
    file.write('minimum spacing 0 0\n')
    file.write('via spacing 0 0\n')
    file.write('0 0 10 10\n')
    file.write('num net {netNum}\n'.format(netNum=netNum))
    # Write nets information 
    pinNum = np.random.randint(2,maxPinNum+1,netNum) # Generate Pin Number randomly
    for i in range(netNum):
        specificPinNum = pinNum[i]
        file.write('A{netInd} 0{netInd} {pin} 1\n'.format(netInd=i+1,pin=specificPinNum))
        xCoordArray = np.random.randint(1,10*gridSize,specificPinNum)
        yCoordArray = np.random.randint(1,10*gridSize,specificPinNum)
        for j in range(specificPinNum):
            file.write('{x}  {y} 1\n'.format(x=xCoordArray[j],y=yCoordArray[j]))
    # Write capacity information
    file.write('{capReduce}'.format(capReduce=capReduce))
    
    file.close()
    return


#  edge_traffic_stat get statiscal information of edge traffic by solving problems
#  with A* search
def edge_traffic_stat(edge_traffic,gridSize):
    via_capacity  = np.zeros((gridSize,gridSize))
    hoz_capacity = np.zeros((gridSize-1,gridSize)) # Only for Layer 1
    vet_capacity = np.zeros((gridSize,gridSize-1)) # Only for Layer 2
    for i in range(edge_traffic.shape[0]):
        connection = edge_traffic[i,:].astype(int)
#        print(connection)
        diff = (connection[3]-connection[0],\
                connection[4]-connection[1],\
                connection[5]-connection[2])
        if diff[0] == 1:
            hoz_capacity[connection[0],connection[1]] \
            = hoz_capacity[connection[0],connection[1]] + 1
        elif diff[0] == -1:
            hoz_capacity[int(connection[0]-1),connection[1]] \
            = hoz_capacity[int(connection[0]-1),connection[1]] + 1
        elif diff[1] == 1:
            vet_capacity[connection[0],connection[1]] \
            = vet_capacity[connection[0],connection[1]] + 1
        elif diff[1] == -1:
            vet_capacity[connection[0],int(connection[1]-1)] \
            = vet_capacity[connection[0],int(connection[1]-1)] + 1
        elif abs(diff[2]) == 1:
            via_capacity[connection[0],connection[1]] \
            = via_capacity[connection[0],connection[1]] + 1
        else:
            continue
    return via_capacity, hoz_capacity, vet_capacity

def parse_arguments():
    parser = argparse.ArgumentParser('Benchmark Generator Parser')
    parser.add_argument('--benchNumber',type=int,\
        dest='benchmarkNumber',default=20)
    parser.add_argument('--gridSize',type=int,dest='gridSize',default=16)
    parser.add_argument('--netNum',type=int,dest='netNum',default=5)
    parser.add_argument('--capacity',type=int,dest='cap',default=4)
    parser.add_argument('--maxPinNum',type=int,dest='maxPinNum',default=5)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    benchmarkNumber = args.benchmarkNumber

    # benchmarkNumber = 20
    savepath = 'benchmark/'  # specify path to save benchmarks
    os.makedirs(savepath)
    os.chdir(savepath)
     
    gridSize = args.gridSize; netNum = args.netNum
    vCap = args.cap; hCap = args.cap; maxPinNum = args.maxPinNum

    for i in range(benchmarkNumber):
        benchmark_name = "test_benchmark_{num}.gr".format(num=i+1)
        generator(benchmark_name,gridSize,netNum,vCap,hCap,maxPinNum,savepath)
    
    
    # Get statistical information about edge traffic by solving benchmarks
    # with A*Star Search
        # initialize edge traffic basket 
        #(data structure: startTile x,y,z and endTile x,y,z )
    edge_traffic =np.empty(shape=(0,6))
    
       # solving problems with A* search
    os.chdir("../benchmark/")
#    benchmarkfile = "test_benchmark_5.gr"
    solution_savepath = '../solutionsForBenchmark/' 
    os.mkdir(solution_savepath)
    for benchmarkfile in os.listdir('.'):
        routeListMerged = solver.solve(benchmarkfile,solution_savepath)
        for netCount in range(len(routeListMerged)):
            for pinCount in range(len(routeListMerged[netCount])-1):
                pinNow = routeListMerged[netCount][pinCount]
                pinNext = routeListMerged[netCount][pinCount+1]
                connection = [int(pinNow[3]),int(pinNow[4]),int(pinNow[2]),\
                              int(pinNext[3]),int(pinNext[4]),int(pinNext[2])]
                edge_traffic = np.vstack((edge_traffic,connection))
    
    # calculate capacity utilization
    print("Total num of edge uitilization: ",edge_traffic.shape[0]) # print total num of edge uitilization
    via_capacity,hoz_capacity,vet_capacity = edge_traffic_stat(edge_traffic,gridSize)
#    
#    print(via_capacity)
#    for i in range(via_capacity.shape[0]):
#        for j in range(via_capacity.shape[1]):
#            print(via_capacity[i,j])
        
     #draw a heat map of capacity utilization

    plt.figure()
    plt.imshow(via_capacity,cmap='hot', interpolation='nearest')
    plt.title('Via Capacity Heatmap')
    os.mkdir('../capacityPlot')
    plt.savefig('../capacityPlot/viaCapacity.jpg')
    
    plt.figure()
    plt.imshow(vet_capacity,cmap='hot', interpolation='nearest')
    plt.title('Vertical Capacity Heatmap (Layer2)')
    plt.savefig('../capacityPlot/vetCapacity.jpg')
    
    plt.figure()
    plt.imshow(hoz_capacity,cmap='hot', interpolation='nearest')
    plt.title('Horizontal Capacity Heatmap (Layer1)')
    plt.savefig('../capacityPlot/hozCapacity.jpg')
    
##    
    
