import numpy as np

from Critic import Critic


class LineCritic(Critic):
    def __init__(self):
        pass


    def critique(self, lvl):
        #Returns a score between 0-1 based on the particular critics scope
        while len(lvl.height_line) < len(lvl.song.height_notes):
            lvl.height_line = [0] + lvl.height_line
        array1 = np.array(lvl.height_line)
        array2 = np.array(lvl.song.height_notes)
        subtracted_array = np.subtract(array1, array2)
        subtracted = list(subtracted_array)

        #Find theoretical max difference between height notes and opposite
        array3 = lvl.max_height - array2
        subtracted_array_max = np.subtract(array3, array2)
        subtracted_max = list(subtracted_array_max)
        return 1-(np.sum(np.square(subtracted))/np.sum(np.square(subtracted_max))) #sum Squared difference


    def print(self):
        print("LINE CRITIC")