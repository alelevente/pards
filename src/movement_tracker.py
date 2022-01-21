'''This module implements a movement tracker object.'''

class MovementTracker:
    movements={}
    
    def __call__(self, t, states, ids, remainings):
        for i,_id in enumerate(ids):
            if _id in self.movements:
                self.movements[_id].append(states[i])
            else:
                self.movements[_id] = [states[i]]
                