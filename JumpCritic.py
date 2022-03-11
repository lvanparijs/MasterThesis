from Critic import Critic


class JumpCritic(Critic): #Difficulty consists of a combination of speed, spikes ratio(CompnentFrequencyCritic), ratio of jump/no_action, and VarietyCritic
    def __init__(self):
        pass

    def critique(self, lvl):
        al = lvl.action_list
        jump_ratio = sum(al)/len(al)
        #Returns a score between 0-1 based on the particular critics scope
        return jump_ratio

    def print(self):
        print("JUMP CRITIC")