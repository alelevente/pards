''' This module implements functions to decide the length of the shared route.'''

import numpy as np

import metrics

def tell_uniform(P, route):
    ''' Selects a random length by sampling a uniform distribution.
        Parameters:
            P: _backward_ transition matrix of the Markov chain
            route: the actual route of a vehicle'''
    assert len(route)>0
    
    r = len(route) if len(route)<2 else np.random.randint(1, len(route), 1)[0]
    return route[-r:]

def tell_min_prob(P, route, o_dist, matrix_power, source_probs):
    ''' Selects the maximal length s.t. the finding probability will be at most as the origin model would dictate
        Parameters:
            P: _backward_ transition matrix of the Markov chain
            route: the actual route of a vehicle
            o_dist: origin distribution
            matrix_power: matrix powering object'''
    assert len(route)>0
    
    r = 1
    #t_r = np.zeros(len(P))
    #t_r[route[-r]] = 1.0
    while (r<len(route)) and (source_probs(route[-r], d=len(route)-r)[route[0]] <= o_dist[route[0]]):
        #t_r[route[-r]] = 0.0
        r += 1
        #if r<len(route):
        #    t_r[route[-r]] = 1.0
    return route[-r:]
        
    
def tell_last_n(P, route, n):
    ''' Selects the last N streets to share.
        Parameters:
            P: _backward_ transition matrix of the Markov chain
            route: the actual route of a vehicle
            n: number of streets to share'''
    assert len(route)>0
    
    streets = 0
    r = 1
    while (r<len(route)-1) and (streets != n):
        prev_street = np.argmax(P[route[-r]])
        if prev_street != route[-(r+1)]:
            streets += 1
        r += 1
    return route[-(r-1):]

def tell_mix(P, route, st_dist, matrix_power, n, source_probs):
    ''' Randomly selects a method from above ones.'''
    assert len(route)>0
    
    method = np.random.choice(np.arange(0, len(n)+2), 1)[0]
    answer = []
    if method == 0:
        answer = tell_uniform(P, route)
    elif method == 1:
        answer = tell_min_prob(P, route, st_dist, matrix_power, source_probs)
    else:
        answer = tell_last_n(P, route, np.random.choice(n, 1)[0]+1)
    return answer