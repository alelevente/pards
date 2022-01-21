'''Module for implementing meetings on the road network'''

import re
import numpy as np

def _get_to_junction(edge_name):
    '''
        Extracts the endpoint of an edge from its name:
        e.g. ABC123XYZ456 -> XYZ456
    '''
    #last element will be the junction name,
    #we shall remove the first character from the result
    return re.findall(r"[0-9][A-Z@]+[0-9]+", edge_name)[-1][1:]

def _collect_neighborings(edge_names):
    '''
        Creates a map from edge names that represent the neighboring edges
        e.g. A2B2 -> [B2A2, B2B3, B2B1, B2C3, A2B2, B3B2, B1B2, C3B2]
    '''
    result = {}
    for e in edge_names:
        result[e] = []
        to_junction = _get_to_junction(e)
        for x in edge_names:
            if x.find(to_junction) >= 0:
                result[e].append(x)
    return result

class Meeting:
    neighbors = {}
    neighbor_indices = {}
    last_meetings = {}
    
    def __init__(self, edge_to_index_map, index_to_edge_map):
        self.neighbors = _collect_neighborings(list(edge_to_index_map.keys()))
        #translating edge names to indices:
        for edge in self.neighbors:
            edge_idx = edge_to_index_map[edge]
            self.neighbor_indices[edge_idx] = [edge_to_index_map[e] for e in self.neighbors[edge]]
        
    def __call__(self, t, states, ids, remainings):
        '''
            Calculates the meeting vehicles. (Implements the a callback function of the simulator)
            Parameters:
                t: timestep
                states: position of vehicles
                ids: ids of the vehicle
                remainings: number of remaining steps
            Returns:
                list of [x,y] pairs, meaning vehicle x meets vehicle y ([x,y] and [y,x] are also contained. Vehicles are members of the actual simulation state, i.e. NOT IDs!)
        '''
        results = []
        for i,s in enumerate(states):
            if s in self.neighbor_indices:
                meetings = np.arange(0,len(states))[np.isin(states, self.neighbor_indices[s])] #ids with whom i car meets
                for m in meetings:
                    #no self meeting, no meeting in last steps:
                    if (i!=m) and ((not str(i)+"_"+str(m) in self.last_meetings)
                                   or (self.last_meetings[str(i)+"_"+str(m)] < t-1)):
                        results.append([i, m])
                        self.last_meetings[str(i)+"_"+str(m)] = t

        
        return results
                
                    
    