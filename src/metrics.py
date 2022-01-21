'''This module implements various metrics to support decision making of
    the information sharing process. Also, it implemets some metrics for evaluation.'''

import numpy as np

import sumolib

from tools.utils import MatrixPower


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
    
    assert (not (p_length is None)) or (not (d is None))
    
    answer = np.array([])
    if not(d is None):
        answer = t_r @ matrix_power(d)
    else:
        elements = []
        for d in range(len(p_length)):
            elements.append(t_r @ matrix_power(d) * p_length[d])
        elements = np.array(elements)
        answer = np.sum(elements, axis=0)
        
    return answer



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


def calculate_correctness_best_n(net, index_to_edge_map, matrix_power: MatrixPower, P_b, route, p_length, starting_edge_index, n=1, ):
    ''' Computes correctness of a malicious alter. 
        Parameters:
            net: SUMO network object
            index_to_edge_map: a transition matrix indices->edge names map
            matrix_power: a MatrixPower object to support calculations
            P_b: transition matrix of the _backward_ Markov chain
            route: the route that ego has shared with alter
            p_length: model of path lengths
            starting_edge_index: the first edge of ego's true route
            n: how many indices to check (in order from best to worst guess)
            
        Returns:
            the distances between the selected N points'''
    
    tr = np.zeros(len(P_b))
    tr[route[0]] = 1.0
    t0 = calculate_source_probability(matrix_power, P_b, tr, p_length = p_length)
    bests = np.argsort(t0)[::-1][:n]
    distances = []
    for b in bests:
        distances.append(_get_distance_between(net, [starting_edge_index, b], index_to_edge_map))
    return distances


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