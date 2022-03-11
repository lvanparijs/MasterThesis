class LevelPiece():

    def __init__(self, pos, boxes, spikes, lava, start_height, end_height):
        self.pos = pos

        boxes_pos = []
        for b in boxes:
            boxes_pos += [b.pos]

        spikes_pos = []
        for s in spikes:
            spikes_pos += [s.pos]

        lava_pos = []
        for l in lava:
            lava_pos += [l.pos]

        self.boxes = boxes_pos
        self.spikes = spikes_pos
        self.lava = lava_pos
        self.start_height = start_height
        self.end_height = end_height

    def get_all_spikes(self):
        return self.spikes

    def get_all_lava(self):
        return self.lava

    def get_all_boxes(self):
        return self.boxes

    def get_last_piece_x(self):
        last_x = 0
        for b in self.boxes:
            if b[0] > last_x:
                last_x = b[0]
        for s in self.spikes:
            if s[0] > last_x:
                last_x = s[0]
        return last_x

