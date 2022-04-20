import numpy as np
import simulation.mc_sampler as sampler

from tqdm import tqdm

class Simulator:
    '''
        Implements the simulator.
        Simulation is based on sampling a Markov Chain.
        The simulator requires a feeding model (describing how new elements are added in time)
        The simulator needs an initial state model (distribution)
        The simulator needs a path-length model (distribution)
        The simulator needs a call-back method.
    '''
    states = np.array([])
    remainings = np.array([])
    ids = np.array([])
    act_id = 0

    def __init__(self, transition_mtx, feeding_model, inital_state_model, path_length_model, terminating_edges=None):
        self.transition_mtx = transition_mtx
        self.feeding_model = feeding_model
        self.initial_state_model = inital_state_model
        self.path_length_model = path_length_model
        self.state_space_size = len(self.initial_state_model)
        self.ids = []
        self.terminating_edges = terminating_edges

    def simulate(self, n_steps=None, callback_function=None):
        '''
            Executes simulation steps.
            Parameters:
                n_steps: the number of steps to execute. If None, execute until completion
                call_back_function(timestep, states): function to call within each simulation step. 
        '''

        def _step(t):
            #adding new elements:
            num_news = int(self.feeding_model[t]) if t<len(self.feeding_model) else 0
            new_states = np.random.choice(range(self.state_space_size),
                num_news,
                p=self.initial_state_model)
            new_states = np.array(new_states, dtype=int)
            new_remainings = np.random.choice(range(len(self.path_length_model)),
                num_news,
                p=self.path_length_model)
            new_ids = np.array(range(self.act_id, self.act_id+num_news))
            
            self.states = np.append(self.states, [new_states])
            self.remainings = np.append(self.remainings, [new_remainings])
            self.ids = np.append(self.ids, [new_ids])
            self.act_id += num_news

            #running the callback:
            #print(max(self.remainings))
            callback_function(t, self.states, self.ids, self.remainings)

            #executing movements:
            self.states = sampler.sample_chain(self.transition_mtx, self.states)
            self.states = np.array(self.states, dtype=int)
            self.remainings = self.remainings - 1 #everyone has stepped one

            #preventing leaving vehicles to reenter:
            if not(self.terminating_edges is None):
                for term in self.terminating_edges:
                    self.remainings[self.states == term] = 1

            #remove finished elements:
            self.states = np.delete(self.states, self.remainings<=0)
            self.ids = np.delete(self.ids, self.remainings<=0)
            self.remainings = np.delete(self.remainings, self.remainings<=0)

        _step(0)
        t = 1
        
        pbar = tqdm(total=n_steps if not(n_steps is None) else len(self.feeding_model)+len(self.path_length_model))
        while ((n_steps is None) and (len(self.states)>0)) or (not(n_steps is None) and (t<n_steps)):
            _step(t)
            t += 1
            pbar.update(1)
        pbar.close()
        
        return t