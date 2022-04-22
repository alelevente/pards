'''This module implements various metrics to support decision making of
    the information sharing process. Also, it implemets some metrics for evaluation.'''

import numpy as np
import networkx as nx

import time

import sumolib

from tools.utils import MatrixPower

import torch

def calculate_source_probability(matrix_power: MatrixPower, P_b, t_r, p_length=None, d=None):
    ''' Computes the distribution of origins in the space of all edges of a network.
        Parameters:
            matrix_power: a MatrixPower object to support calculations
            P_b: transition matrix of the _backward_ Markov chain
            t_r: one-hot encoded vector, representing the meeting point
            p_length: model of path lengths
            d: true length of the path.
            
        This function can compute distribution of both p(t0 | P_b, t_r, p_length) (alter) and
        p(t0 | P_b, t_r, d) (ego). Hence, either p_length or d parameter shall be defined.'''
    
    #assert (not (p_length is None)) or (not (d is None))
    
    answer = np.array([])
    if not(d is None):
        answer = t_r @ matrix_power(d)
    else:
        elements = []
        for d in range(len(p_length)):
            t_start = time.time()
            elements.append(t_r @ matrix_power(d) * p_length[d])
            #elements.append(np.dot(t_r, matrix_power(d))*p_length[d])
            print(time.time()-t_start)
        elements = np.array(elements)
        answer = np.sum(elements, axis=0)
        
    return answer

class SourceProbabilities:
    ''' Supports fast calculation of origin distributions by precalculating the results for each
        edges.'''
    def __init__(self, matrix_power: MatrixPower, P_b, p_length):
        self.alter_sources = {}
        self.ego_sources = {}
        
        cuda = torch.cuda.is_available()
        mp = []
        if cuda:
            for d in range(len(p_length)):
                mp.append(torch.from_numpy(matrix_power(d)).float().to("cuda"))
                
        for edge_idx in range(len(P_b)): #iterating through each edges:
            self.ego_sources[edge_idx] = []
            t_r = torch.zeros(len(P_b)) if torch.cuda.is_available() else np.zeros(len(P_b))
            t_r[edge_idx] = 1.0
            if cuda:
                t_r = t_r.float().to("cuda")
            #calculation
            elements = []
            for d in range(len(p_length)):
                if cuda:
                    with torch.no_grad():
                        #mp = torch.from_numpy(matrix_power(d)).float().to("cuda")
                        elem_ = (t_r @ mp[d]).to("cpu").numpy()
                else:
                    elem_ = t_r @ matrix_power(d)
                self.ego_sources[edge_idx].append(elem_)
                elements.append(elem_ * p_length[d])
            elements = np.array(elements)
            self.alter_sources[edge_idx] = np.sum(elements, axis=0)
            
        print("Source probabilities have been calculated.")
            
    def __call__(self, known_edge, d=None):
        #if not(d is None): print(d)
        return self.alter_sources[known_edge] if d is None else self.ego_sources[known_edge][d]



def _get_distance_between(net, indices, index_to_edge_map):
    ''' Calculate the distance between two indices in the network
        Parameters:
            net: SUMO network
            indices: list of two indices
            index_to_edge_map: a transition matrix indices->edge names map
        Returns:
            minimum of driving distances between the two points'''
    
    if (not(indices[0] in index_to_edge_map)) or (not (indices[1] in index_to_edge_map)):
        return float('inf')

    edge_1 = net.getEdge(index_to_edge_map[indices[0]])
    edge_2 = net.getEdge(index_to_edge_map[indices[1]])
    x_y = net.getShortestPath(edge_1, edge_2)
    y_x = net.getShortestPath(edge_2, edge_1)
    d1 = x_y[1]
    d2 = y_x[1]
    return min([d1, d2])

class DistanceCalculator:
    '''Class for fast calculation of distances in a network'''
    def __init__(self, P):
        ''' Parameters:
            P: _forward_ transition matrix'''
        graph = nx.DiGraph()
        graph.add_nodes_from(range(len(P)))
        for i in range(len(P)):
            for j in range(len(P)):
                if P[i][j] > 0: graph.add_edge(i,j)
                
        self.length = dict(nx.all_pairs_dijkstra_path_length(graph))
        #print(self.length)
        
    def __call__(self, x, y):
        return min(self.length[x][y], self.length[y][x])


def calculate_correctness_best_n(net, index_to_edge_map, matrix_power: MatrixPower, P_b, route, p_length, starting_edge_index, source_probs, n=1, distance_calculator=None,):
    ''' Computes correctness of a malicious alter. 
        Parameters:
            net: SUMO network object
            index_to_edge_map: a transition matrix indices->edge names map
            matrix_power: a MatrixPower object to support calculations
            P_b: transition matrix of the _backward_ Markov chain
            route: the route that ego has shared with alter
            p_length: model of path lengths
            starting_edge_index: the first edge of ego's true route
            source_probs: precomputed probabilities of origin edges (for faster run)
            n: how many indices to check (in order from best to worst guess)
            distance_calculator: a distance calculator object (for faster run)
            
        Returns:
            the distances between the selected N points'''
    
    assert len(route)>0
    
    #tr = np.zeros(len(P_b))
    #tr[route[0]] = 1.0
    times = {"source_p": 0, "distances": 0}
    t_start = time.time()
        
    t0 = source_probs(known_edge = route[0])
    tc_0 = source_probs(known_edge = route[-1])
    times["source_p"] = time.time()-t_start
    bests = np.argsort(t0)[::-1][:n]
    bests_tc = np.argsort(tc_0)[::-1][:n]
    distances = []
    dist_differences = []
    t_start = time.time()
    for i, b in enumerate(bests):
        if distance_calculator is None:
            distances.append(_get_distance_between(net, [starting_edge_index, b], index_to_edge_map))
        else:
            distances.append(distance_calculator(starting_edge_index, b))
            dist_differences.append(distance_calculator(starting_edge_index, b)-
                                    distance_calculator(starting_edge_index, bests_tc[i]))
    times["distances"] = time.time() - t_start
    return distances, dist_differences, times


def compute_iong(actual_route, gathered_information):
    ''' Computes the Information-Otherwise-Not-Gained metric
        Parameters:
            actual_route: list of the edges along a route of a vehicle
            gathered_information: list of the received edges
        Returns:
            the number of edges that are received but not visited: |gathered_information\actual_route|'''
    
    actual = set(actual_route)
    gathered = set(gathered_information)
    return len(gathered.difference(actual))
