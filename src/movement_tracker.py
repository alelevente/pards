'''This module implements a movement tracker object.'''

class MovementTracker:
    
    def __init__(self):
        self.movements = {}
    
    def __call__(self, t, states, ids, remainings):
        for i,_id in enumerate(ids):
            if _id in self.movements:
                self.movements[_id].append(int(states[i]))
            else:
                self.movements[_id] = [int(states[i])]
                