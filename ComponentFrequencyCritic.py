from Critic import Critic


class ComponentFrequencyCritic(Critic): #Scores a level based on the spike/obstacle ratio and the genre
    def __init__(self):
        pass

    def critique(self, lvl):
        #['Blues', 'Classical', 'Electronic', 'Jazz', 'Rap', 'Rock'] [0.2-0.3,0-0.1,0.3-0.4,0.1-0.2,0.5-0.6,0.4-0.5]
        #Returns a score between 0-1 based on the particular critics scope
        spike_ratio = len(lvl.get_all_spikes())/len(lvl.get_all_boxes())
        print("SPIKE RATIO")
        print(spike_ratio)
        if lvl.song.genre == 'Blues':
            return 1-((spike_ratio-0.25)**2) #Distance squared, favouring closer to 0.25
        elif lvl.song.genre == 'Classical':
            return 1-((spike_ratio - 0.05) ** 2)
        elif lvl.song.genre == 'Electronic':
            return 1-((spike_ratio - 0.35) ** 2)
        elif lvl.song.genre == 'Jazz':
            return 1-((spike_ratio - 0.15) ** 2)
        elif lvl.song.genre == 'Rap':
            return 1-((spike_ratio - 0.75) ** 2)
        elif lvl.song.genre == 'Rock':
            return 1-((spike_ratio - 0.55) ** 2)

    def print(self):
        print("COMPONENT FREQUENCY CRITIC")