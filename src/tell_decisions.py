''' This module implements functions to decide the length of the shared route.'''

import numpy as np

import metrics

def tell_uniform(P, route):
    ''' Selects a random length by sampling a uniform distribution.
        Parameters:
            P: _backward_ transition matrix of the Markov chain
            route: the actual route of a vehicle'''
    r = len(route) if len(route)<2 else np.random.randint(1, len(route), 1)[0]
    return route[-r:]

def tell_min_prob(P, route, st_dist, matrix_power):
    ''' Selects the maximal length s.t. the finding probability will be at most as it would be in the stationary case.
        Parameters:
            P: _backward_ transition matrix of the Markov chain
            route: the actual route of a vehicle
            st_dist: stationary distribution of the _forward_ Markov chain
            matrix_power: matrix powering object'''
    r = 1
    t_r = np.zeros(len(P))
    t_r[route[-r]] = 1.0
    while (r<len(route)) and (metrics.calculate_source_probability(matrix_power, P, t_r, d=r)[route[-r]] <= st_dist[route[-r]]):
        t_r[route[-r]] = 0.0
        r += 1
        if r<len(route):
            t_r[route[-r]] = 1.0
    return route[-r:]
        
    
def tell_last_n(P, route, n):
    ''' Selects the last N streets to share.
        Parameters:
            P: _backward_ transition matrix of the Markov chain
            route: the actual route of a vehicle
            n: number of streets to share'''
    streets = 0
    r = 1
    while (r<len(route)-1) and (streets != n):
        prev_street = np.argmax(P[route[-r]])
        if prev_street != route[-(r+1)]:
            streets += 1
        r += 1
    return route[-(r-1):]

def tell_mix(P, route, st_dist, matrix_power, n):
    ''' Randomly selects a method from above ones.'''
    method = np.random.choice([0,1,2], 1)[0]
    answer = []
    if method == 0:
        answer = tell_uniform(P, route)
    elif method == 1:
        answer = tell_min_prob(P, route, st_dist, matrix_power)
    else:
        answer = tell_last_n(P, route, n)
    return answer