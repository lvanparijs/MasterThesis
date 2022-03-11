class Critic:

    def __init__(self):
        #init Critic
        pass

    def critique(self, lvl):
        #Returns a score between 0-1 based on the particular critics scope
        return

    def print(self):
        print("CRITIC")

class FeasibilityCritic(Critic): #Level always feasible, max_jump height compared to used jumps(1_up or 2_up)
    def __init__(self):
        super.__init__()

    def critique(self, lvl):
        #Returns a score between 0-1 based on the particular critics scope
        return


class SynchronisityCritic(Critic): #Combines LineCritic and ComponentFrequencyCritic
    def __init__(self):
        super.__init__()

    def critique(self, lvl):
        #Returns a score between 0-1 based on the particular critics scope
        return
