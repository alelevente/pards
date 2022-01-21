import numpy as np

def sample_chain(P_mc, states):
    '''Samples a Markov Chain'''
    return [np.random.choice(range(len(P_mc)), 1, p = P_mc[int(state)])[0]
        for state in states]