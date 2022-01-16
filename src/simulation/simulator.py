import numpy as np
import mc_sampler as sampler

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

    def __init__(self, transition_mtx, feeding_model, inital_state_model, path_length_model):
        self.transition_mtx = transition_mtx
        self.feeding_model = feeding_model
        self.initial_state_model = inital_state_model
        self.path_length_model = path_length_model
        self.state_space_size = len(self.initial_state_model)

    def simulate(self, n_steps=None, call_back_function=None):
        '''
            Executes simulation steps.
            Parameters:
                n_steps: the number of steps to execute. If None, execute until completion
                call_back_function(timestep, states): function to call within each simulation step. 
        '''

        def _step(t):
            #adding new elements:
            new_states = np.choice(range(self.state_space_size),
                self.feeding_model[t] if t<len(self.feeding_model) else 0,
                p=self.initial_state_model)
            new_remainings = np.choice(range(len(self.path_length_model)),
                self.feeding_model[t] if t<len(self.feeding_model) else 0,
                p=self.path_length_model)
            
            self.states = np.append(self.states, [new_states])
            self.remainings = np.append(self.remainings, [new_remainings])

            #running the callback:
            call_back_function(t, self.states)

            #executing movements:
            self.states = sampler.sample_chain(self.transition_mtx, self.states)
            self.remainings = self.remainings - 1 #everyone has stepped one

            #remove finished elements:
            self.states = np.delete(self.states, self.remainings==0)
            self.remainings = np.delete(self.remainings, self.remainings==0)

        _step(0)
        t = 1
        while ((n_steps is None) and (len(self.states)>0) or
            (t<n_steps)):
            _step(t)
            t += 1
        return t