'''Sampling a Markov Chain'''

import numpy as np

def sample_chain(P_mc, states):
    return [np.choice(np.range(len(P_mc)), 1, p = P_mc[state])[0]
        for state in states]