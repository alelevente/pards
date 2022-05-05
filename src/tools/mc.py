'''Methods to handle SUMO networks as Markov Chains (MCs)'''

import numpy as np
import pandas as pd
from sklearn.preprocessing import normalize

import sumolib

##############################################################
################ METHODS FOR PREPROCESSING ###################
def read_MC(network_path: str, turning_path: str, default_turning_rates: list):
    '''
        Reads a SUMO network and the turning description file. Then converts them into a MC.
        Parameters:
            network_path: path to the SUMO road network file
            turning_path: path to the turning definition file
        Return:
            P: transition matrix of the MC
            edge_to_index_map: network edges -> indices of P
            index_to_edge_map: indices of P -> network edges
    '''
    
    net = sumolib.net.readNet(network_path)
    turning_desc = pd.read_xml(turning_path, xpath="./interval/*")
    return create_transition_matrix(net, default_turning_rates, turning_desc)


def get_turn_probabilities(from_edge, turning_rates, special_turning_rates=None):
    '''
        Creates a map of connection objects to probabilities of turning from a given a edge.
        Parameters:
            from_edge: a given edge of the SUMO road network
            turning_rates: default turning rates in the network
            special_turning_rates: some edges may have special turning rates
        Please note, if a `from_edge` is special, it shall be accurately and completly specified in special_turning_rates!'''

    from_id = from_edge._id
    answer = {}
    turning_rates_ = turning_rates[:] #copy
    DIRECTION_LIST = ["r", "R", "s", "L", "l", "t"]
    connections = list(from_edge.getOutgoing().values())
    
    #special turning rates:
    if (not(special_turning_rates is None)) and (from_id in special_turning_rates["from"].values):
        processed_directions = [] #removes the duplicated connections
        rates = special_turning_rates[special_turning_rates["from"] == from_id]
        for c in connections:
            for d in c:
                direction = d.getDirection()
                if not(direction in processed_directions):
                    to_id = d.getTo()._id
                    processed_directions.append(direction)
                    #print(from_id, to_id)
                    answer[d] = rates[rates["to"] == to_id].probability.values[0]
        return answer
    
    #normal turning rates:
    directions = {}
    for c in connections:
        for d in c:
            directions[d.getDirection()]=d
    if len(directions)<len(turning_rates): #grouping all remaining probabilities into the leftmost direction:
        turning_rates_[len(directions)-1] = np.sum(turning_rates[len(directions)-1:])
    
    turn_idx = 0
    for d in DIRECTION_LIST:
        if d in directions:
            answer[directions[d]]= turning_rates_[turn_idx]
            turn_idx += 1
    return answer

def create_transition_matrix(net, turning_rates, special_turning_rates):
    """
        Creates the MCtransition matrix from a SUMO network,
        given the turning rates, and special turning rates.

        Parameters:
            net: a SUMO road network object
            turning_rates: list defining the default turning rates
            special_turning_rates: definition of special turning rates
    
        Returns the transition matrix, the dictionary of edge indices to the
        coordinates of P, and also its inverse."""
    
    edge_to_index_map = {}
    index_to_edge_map = {}
    P = np.zeros([len(net._edges), len(net._edges)])
    
    for edge in net.getEdges():
        probs = get_turn_probabilities(edge, turning_rates, special_turning_rates)
        if not(edge._id) in edge_to_index_map:
            edge_to_index_map[edge._id] = len(edge_to_index_map)
            index_to_edge_map[len(index_to_edge_map)] = edge._id
        for conn in probs:
            to_edge = conn.getTo()
            if not(to_edge._id) in edge_to_index_map:
                edge_to_index_map[to_edge._id] = len(edge_to_index_map)
                index_to_edge_map[len(index_to_edge_map)] = to_edge._id
            P[edge_to_index_map[edge._id], edge_to_index_map[to_edge._id]] = probs[conn]
    return P, edge_to_index_map, index_to_edge_map

def list_terminating_edges(trans_mtx):
        #an edge is a terminating edge, iff no edges go out from that
        terminating_edges = []
        for i in range(len(trans_mtx)):
            if np.sum(trans_mtx[i, :]) == 0:
                terminating_edges.append(i)
        return terminating_edges

# Methods for creating an irreducible, positive MC
# Construction:
# 1. Adding a new source/terminal (ST) state to the chain
# 2. Every terminal nodes will connect to this ST node with 1.0 probability.
# 3. From the ST node, edges will point to starting edges of the network with custom probabilities.
#
# Consequently:
# - Possible to select the direction of the traffic.
# - Possible to be outside of the network.
# - Satisfying the condiitions of the existance of a unique stationary distribution.

def add_st_node(P, source_distribution=None):
    '''
        Adds a source/terminal (ST) node to a MC given by its transition matrix.
        Parameters:
            P: transition matrix of a MC
            source_distribution: a distribution,
            describing the probabilities of stepping from the ST to the source nodes.
    '''

    #helper functions:
    def list_source_edges(trans_mtx):
        #an edge is a source edge, iff no edges come into that
        source_edges = []
        for i in range(len(trans_mtx)):
            if np.sum(trans_mtx[:, i]) == 0:
                source_edges.append(i)
        return source_edges

    def connect_terminates_to_ST(trans_mtx):
        terms = list_terminating_edges(trans_mtx)
        new_column = np.zeros(len(trans_mtx)).reshape(len(trans_mtx), 1)
        for i in terms:
            new_column[i]=1.0
        #adding a new column to the original transition matrix:
        return np.append(trans_mtx, new_column, axis=1) if np.sum(new_column)>0 else trans_mtx

    def connect_sources_to_ST(trans_mtx, distribution=None):
        new_row = np.zeros(len(trans_mtx)+1)
        add_new_row = False
        if distribution is None:
            sources = list_source_edges(trans_mtx)
            p_source = 1/len(sources) if len(sources)>0 else 0
            add_new_row = len(sources)>0
            for i in sources:
                new_row[i] = p_source
        else:
            new_row = distribution
            add_new_row = True
        #adding a new row to the original transition matrix:
        return np.vstack((trans_mtx, new_row)) if add_new_row else trans_mtx


    #outer function:
    P_a = connect_terminates_to_ST(P)
    P_a = connect_sources_to_ST(P_a, source_distribution)
    return P_a

#########################################
####### STATIONARY DISTRIBUTION #########

def calculate_stationary_distribution(P):
    P2 = P.T - np.eye(len(P))
    P2[-1] = np.ones(len(P))
    return np.linalg.solve(P2, np.concatenate((np.zeros(len(P2)-1), [1])))


#########################################
####### CREATE TIME REVERSED MC #########
def calculate_time_reversed_mc(P, π):
    '''
        Creates the time reversed version of the MC.
        Parameters:
            P: defines the transition matrix of the MC
            pi: defines the stationary distribution of the MC
    '''
    Π = np.tile(π, (len(π), 1)).T #a matrix filled with pi
    P_inv = P.T * Π #simply calculating the reversed version
    P_inv = normalize(P_inv, "l1")
    return P_inv