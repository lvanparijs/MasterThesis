from Critic import Critic


class SpeedCritic(Critic): #Difficulty consists of a combination of speed, spikes ratio(CompnentFrequencyCritic), ratio of jump/no_action, and VarietyCritic
    def __init__(self):
        pass

    def critique(self, lvl):
        speed_ratio = lvl.song.tempo/200 #200BPM is insane hardstyle techno, will be the highest "possible" tempo in this project
        return speed_ratio

    def print(self):
        print("SPEED CRITIC")