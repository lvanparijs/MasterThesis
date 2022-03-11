from Critic import Critic


class EmptynessCritic(Critic):
    def __init__(self):
        pass


    def critique(self, lvl):
        #MEASURE DENSITY OF OBJECTS AS AN EMPTYNESS CRITIC
        filled_pieces = 0
        num_pieces = len(lvl.get_pieces())
        if num_pieces > 0:
            for p in lvl.get_pieces():
                if len(p.boxes) > 0 or len(p.spikes) > 0: #Not empty piece
                    filled_pieces += 1
            return filled_pieces/len(lvl.get_pieces())
        else: #If level is empty return 0
            return 0


    def print(self):
        print("EMPTYNESS CRITIC")