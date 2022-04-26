'''MeasCallback class implements a callback functor for the simulation. It
handles the meeting and the information sharing functions. '''

import meeting_model
import movement_tracker
import tell_decisions
import metrics

import time

class DistanceRecords:
    '''Stores distance measurements.'''
    def __init__(self):
        ''' Parameters:
            method_names: names of the records'''
        self.ids = []
        self.method = []
        self.distances = []
        self.distance_diffs = []
        self.times = []


class MeasCallback:
    def __init__(self, net, P_f, P_b, edge_to_index_map, index_to_edge_map,
                 o_dist, matrix_power,
                 p_length,
                 mix_n = [1,2,3]):
        '''
            Parameters:
                net: SUMO road network
                P_f: forward transition matrix of the Markov Chain
                P_b: backward transition matrix of the Markov Chain
                edge_to_index_map: network edges -> indices of P
                index_to_edge_map: indices of P -> network edges
                o_dist: origin distribution of the _forward_ Markov Chain
                matrix_power: matrix poewring object
                p_length: route length model
                mix_n: n values for the MIX data selection method
        '''
        self.net = net
        self.meeting_model = meeting_model.Meeting(edge_to_index_map, index_to_edge_map)
        self.P = P_b
        self.o_dist = o_dist
        self.matrix_power = matrix_power
        self.index_to_edge_map = index_to_edge_map
        self.p_length = p_length
        self.mix_n = mix_n
        
        self.movement_tracker = movement_tracker.MovementTracker()
        
        self.received_information_uniform = {}
        self.received_information_minprob = {}
        self.received_information_last1 = {}
        self.received_information_last2 = {}
        self.received_information_last3 = {}
        self.received_information_mix = {}
        
        self.times = {"dist_calc": 0, "tell_calc": 0, "meetings": 0, "source_p": 0, "distances": 0}
        
        self.distance_calculator = metrics.DistanceCalculator(P_f)
        self.source_probs = metrics.SourceProbabilities(matrix_power, P_b, p_length)
        self.distance_records = DistanceRecords()
        
        
    def _store_distances(self, t, sender_id, sent_routes, method_names, true_starting_edge, n=10):
        '''
            Stores the correctness (i.e. reconstruction distances) of alter. This can be
            seen as the privacy loss of ego.
            Parameters:
                t: timestep
                sender_id: id of the sender vehicle (ego)
                sent_route: list of lists of the sent edges per measurement cases
                   (in order of time, i.e. sent_route[0] is the firstly edge
                   visited, sent_route[-1] is the point of sharing)
                method_names: name of the sent_route selection methods
                true_starting_edge: origin of the sender vehicle (ego)
                n: number of most probable edges
            Stores:
                distances[id][t][x] refers to the top n distances of the given vehicle id
                shared at timestep t. x iterates through the telling methods
        '''
        time_start = time.time()
        for route, name in zip(sent_routes, method_names):
            dist_, dist_dif, times = metrics.calculate_correctness_best_n(self.net, self.index_to_edge_map,
                                                             self.matrix_power,
                                                             self.P, route, self.p_length,
                                                             true_starting_edge,
                                                             self.source_probs,
                                                             n=n,
                                                             distance_calculator = self.distance_calculator)
            
            self.times["source_p"] = self.times["source_p"] + times["source_p"]
            self.times["distances"] = self.times["distances"] + times["distances"]
            for i in range(n):
                self.distance_records.ids.append(sender_id)
                self.distance_records.times.append(t)
                self.distance_records.method.append(name)
                self.distance_records.distances.append(dist_[i])
                self.distance_records.distance_diffs.append(dist_dif[i])
            
        self.times["dist_calc"] = self.times["dist_calc"] + (time.time()-time_start)
        
        
    def _share_information(self, t, ids, routes):
        '''
            This method handles the information sharing among two vehicles.
            Parameters:
                t: timestep
                ids: ids of the two vehicles
                routes: routes of the vehicles
        '''
        assert (len(ids) == 2) and (len(routes) == 2)
        
        #calculating the amount of shared information:
        uniform = [[],[]]
        minprob = [[],[]]
        last1   = [[],[]]
        last2   = [[],[]]
        last3   = [[],[]]
        mix     = [[],[]]
        
        t_start = time.time()
        for i,_id in enumerate(ids):
            uniform[i]= tell_decisions.tell_uniform(self.P, routes[i])
            minprob[i]= tell_decisions.tell_min_prob(self.P, routes[i], self.o_dist, self.matrix_power, self.source_probs)
            last1[i]= tell_decisions.tell_last_n(self.P, routes[i], 1)
            last2[i]= tell_decisions.tell_last_n(self.P, routes[i], 2)
            last3[i]= tell_decisions.tell_last_n(self.P, routes[i], 3)
            mix[i]= tell_decisions.tell_mix(self.P, routes[i], self.o_dist, self.matrix_power, self.mix_n, self.source_probs)
        
        self.times["tell_calc"] = self.times["tell_calc"] + (time.time()-t_start)
            
        #print(uniform[i],"\n", minprob[i], "\n", last1[i])
        
        #storing results:
        for i,_id in enumerate(ids):
            if not(_id in self.received_information_uniform):
                self.received_information_uniform[_id] = []
                self.received_information_minprob[_id] = []
                self.received_information_last1[_id] = []
                self.received_information_last2[_id] = []
                self.received_information_last3[_id] = []
                self.received_information_mix[_id] = []
            #stroring results, note that the calculated shared information of ego vehicle is the received information by alter
            self.received_information_uniform[_id] = self.received_information_uniform[_id] + uniform[i-1]
            self.received_information_minprob[_id] = self.received_information_minprob[_id] + minprob[i-1]
            self.received_information_last1[_id] = self.received_information_last1[_id] + last1[i-1]
            self.received_information_last2[_id] = self.received_information_last2[_id] + last2[i-1]
            self.received_information_last3[_id] = self.received_information_last3[_id] + last3[i-1]
            self.received_information_mix[_id] = self.received_information_mix[_id] + mix[i-1]
            #storing distances = the loss of privacy caused by the sharing:
            self._store_distances(t, _id,
                    [uniform[i-1], minprob[i-1], last1[i-1], last2[i-1], last3[i-1], mix[i-1]],
                    ["uniform", "minprob", "last1", "last2", "last3", "mix"],
                                  self.movement_tracker.movements[_id][0])
            
        
    def __call__(self, t, states, ids, remainings):
        #if t%20 == 0: print("Step %d"%t)
        self.movement_tracker(t, states, ids, remainings)
        t_start = time.time()
        meetings = self.meeting_model(t, states, ids, remainings)
        self.times["meetings"] = self.times["meetings"] + (time.time()-t_start)
        for x,y in meetings:
            route_x = self.movement_tracker.movements[ids[x]]
            route_y = self.movement_tracker.movements[ids[y]]
            
            #sharing information:
            self._share_information(t, [ids[x],ids[y]], [route_x, route_y]) 
