import copy
import random

import pygame

from Box import Box
from Lava import Lava
from LevelPiece import LevelPiece
from Platform import Platform
from Spike import Spike

vec = pygame.math.Vector2
BOX_SIZE = 40
JUMP = 1
NO_ACTION = 0


class Level:

    ##A level is essentially a collection of obstacles, the ground is always the same, created based on a music track

    def __init__(self, song, height, player, lvl_pieces, screen_height, action_list):
        self.start_buffer = 400
        self.screen_height = screen_height
        if song is None: #For Main Menu
            self.width = 640
            self.tempo = 0
        else:

            self.song = song
            self.action_list = action_list  # Initialise list of Actions
            self.height_line = []  # Level height line, used for Critic

            self.width = song.song_duration * player.max_vel * 60  # Width of the level in pixels, determined by length of song, speed of player

            if len(lvl_pieces) == 0: #No content yet, get genre for generating afterwards
                # Set player parameters
                player.pixels_per_second = int((5 * BOX_SIZE) / self.song.spb)  # Desired jump distance
                player.set_velocity(player.pixels_per_second)  # Set velocity based on the desired jump length
                player.parameter_tuning(5)  # Tune the gravity and jump speed to fit withing

        self.player = player
        self.height = height #Height of the level

        self.max_height = 6 #Max level height

        self.pieces = lvl_pieces #Set the level pieces

        self.height_line = self.get_height_line()

        #Extract the individual objects from the pieces, if there are any
        self.boxes = list()
        self.spikes = list()
        self.lava = list()

        for p in self.pieces:
            self.boxes += p.get_all_boxes()[:]
            self.spikes += p.get_all_spikes()[:]
            self.lava += p.get_all_lava()[:]


        #Initialise the sprites of the objects, neccesary for collision detection and drawing
        self.boxes_objects = pygame.sprite.Group()
        self.spikes_objects = pygame.sprite.Group()
        self.lava_objects = pygame.sprite.Group()

        for b in self.boxes:
            self.boxes_objects.add(Box(b))

        for s in self.spikes:
            self.spikes_objects.add(Spike(s))

        for l in self.lava:
            self.lava_objects.add(Lava(l))

        self.box_frequency = 2 #Amount of boxes per 100 pixels, for random generation
        self.spike_frequency = 1 #Amount of spikes per 100 pixels
        self.ground_level = int(screen_height * 0.9)#Ground level
        self.platform = Platform(vec(0, self.ground_level),self.width) #Main platform of the level
        self.boxes_objects.add(self.platform)
        self.finish_flag = (self.width - 300, self.ground_level+35) #Positioning finish flag

    def choose_level_piece(self,pos, start_height,end_height):
        bxes = []
        spks = []
        lva = []

        if start_height > end_height:
            if random.uniform(0,1) > 0.5: #Equal chance of replacing
                bxes,spks,lva = self.jump_down(pos, start_height)
            else:
                bxes,spks,lva = self.fall_down(pos, start_height)
        elif start_height < end_height:

            bxes,spks,lva = self.jump_up_1(pos,start_height)
        else: #Equal height, so pick flat piece
            if start_height <= 0: #On ground
                choose = random.randint(0, 4)
                if choose == 0:
                    bxes, spks, lva = self.spikes_flat_1(pos, start_height)
                elif choose == 1:
                    bxes, spks, lva = self.spikes_flat_2(pos, start_height)
                elif choose == 2:
                    bxes, spks, lva = self.spikes_flat_3(pos, start_height)
                else:
                    bxes, spks, lva = [], [], []
            else:
                choose = random.randint(0,4)
                if choose == 0:
                    bxes,spks,lva = self.flat_blocks(pos,start_height)
                elif choose == 1:
                    bxes,spks,lva = self.flat_blocks_spike_1(pos,start_height)
                elif choose == 2:
                    bxes,spks,lva = self.flat_blocks_spike_2(pos,start_height)
                else:
                    bxes,spks,lva = self.flat_blocks_spike_3(pos,start_height)
        return LevelPiece(pos,bxes,spks,lva,start_height,end_height)


    def get_pieces(self):
        return self.pieces

    def get_pieces_in_range(self, start_x, end_x):
        selected = []
        for p in self.pieces:
            pos = p.pos
            if start_x <= pos <= end_x: #Set bounds for selection
                selected += [p]
        return selected

    def get_platform(self):
        return self.platform

    def get_lvl_data(self):
        return self.boxes,self.spikes

    def get_height_line(self):
        height_line = list()
        for p in self.pieces:
            height_line += [p.end_height]
        return height_line

    def flatten(self):
        cur_height = 0
        piece_id = 0
        piece1 = LevelPiece(0, [], [], [], cur_height, cur_height)
        piece2 = self.pieces[piece_id] #Grab first piece
        new_pieces_list = copy.deepcopy(self.pieces)
        #print(piece1.end_height)
        while piece2.start_height > piece1.end_height:
            #Switch pieces
            bx,sp,lv = self.jump_up_1(piece2.pos,piece1.end_height)
            new_piece = LevelPiece(piece2.pos,bx,sp,lv,piece1.end_height,piece1.end_height+1)
            new_pieces_list[piece_id] = new_piece
            piece_id += 1
            piece1 = new_piece
            piece2 = self.pieces[piece_id]
        #Return the new level
        return Level(self.song, self.height, self.player, new_pieces_list, self.screen_height, self.action_list)


    def generate_geometry_from_grammar_rnd(self,vel):
        print("GENERATING GEOMETRY...")
        obstacle_pos = self.song.beat_times * vel * 60 + self.start_buffer #Initialise the beginning of each level piece
        height_cnt = 0 #Floor == 0
        self.height_line = [0]
        self.pieces += [LevelPiece(obstacle_pos[0], [], [], [], height_cnt, height_cnt)] #Start with empty piece

        for i in range(1, len(obstacle_pos)): #For each possible obstacle location
            if self.action_list[i]:  # Jump
                rnd_direction = random.uniform(0, 1) #Randomise the directions
                if rnd_direction > 0.67: #UP
                    bxs, spk, lva = self.jump_up_1(obstacle_pos[i], height_cnt)
                    self.pieces += [LevelPiece(obstacle_pos[i], bxs, spk, lva, height_cnt, height_cnt + 1)]
                    height_cnt += 1
                elif rnd_direction > 0.33: #FLAT
                    if height_cnt > 0: #off the floor
                        rnd_threshold = random.uniform(0,1)
                        if random.uniform(0,1) > rnd_threshold: #Randomly choose between lava or spikes
                            bxs,spk,lva = self.flat_jump_lava(obstacle_pos[i],height_cnt)
                            self.pieces += [LevelPiece(obstacle_pos[i], bxs, spk, lva, height_cnt, height_cnt)]
                        else:
                            n_spikes = random.randint(1,3)
                            if n_spikes == 1:
                                bxs,spk,lva = self.flat_blocks_spike_1(obstacle_pos[i],height_cnt)
                                self.pieces += [LevelPiece(obstacle_pos[i], bxs, spk, lva, height_cnt, height_cnt)]
                            elif n_spikes == 2:
                                bxs,spk,lva = self.flat_blocks_spike_2(obstacle_pos[i],height_cnt)
                                self.pieces += [LevelPiece(obstacle_pos[i], bxs, spk, lva, height_cnt, height_cnt)]
                            elif n_spikes == 3:
                                bxs,spk,lva = self.flat_blocks_spike_3(obstacle_pos[i],height_cnt)
                                self.pieces += [LevelPiece(obstacle_pos[i], bxs, spk, lva, height_cnt, height_cnt)]
                    else: #on the floor
                        height_cnt = 0
                        n_spikes = random.randint(1,3) #Randomly select the number of spikes
                        if n_spikes == 1:
                            bxs,spk,lva = self.spikes_flat_1(obstacle_pos[i], height_cnt)
                            self.pieces += [LevelPiece(obstacle_pos[i], bxs, spk, lva, height_cnt, height_cnt)]
                        elif n_spikes == 2:
                            bxs,spk,lva = self.spikes_flat_2(obstacle_pos[i], height_cnt)
                            self.pieces += [LevelPiece(obstacle_pos[i], bxs, spk, lva, height_cnt, height_cnt)]
                        elif n_spikes == 3:
                            bxs,spk,lva = self.spikes_flat_3(obstacle_pos[i], height_cnt)
                            self.pieces += [LevelPiece(obstacle_pos[i], bxs, spk, lva, height_cnt, height_cnt)]

                else: #DOWN and on the floor = FLAT action
                    if height_cnt > 0: #If off the floor, jump down
                        bxs,spk,lva = self.jump_down(obstacle_pos[i], height_cnt)
                        self.pieces += [LevelPiece(obstacle_pos[i], bxs, spk, lva, height_cnt, height_cnt-1)]
                        height_cnt -= 1
                    else:
                        height_cnt = 0
                        n_spikes = random.randint(1,3) #Randomly select the number of spikes to be placed
                        if n_spikes == 1:
                            bxs,spk,lva = self.spikes_flat_1(obstacle_pos[i], height_cnt)
                            self.pieces += [LevelPiece(obstacle_pos[i], bxs, spk, lva, height_cnt, height_cnt)]
                        elif n_spikes == 2:
                            bxs,spk,lva = self.spikes_flat_2(obstacle_pos[i], height_cnt)
                            self.pieces += [LevelPiece(obstacle_pos[i], bxs, spk, lva, height_cnt, height_cnt)]
                        elif n_spikes == 3:
                            bxs,spk,lva = self.spikes_flat_3(obstacle_pos[i], height_cnt)
                            self.pieces += [LevelPiece(obstacle_pos[i], bxs, spk, lva, height_cnt, height_cnt)]

            else:
                rnd_direction = random.uniform(0, 1)  # Randomise the directions
                if rnd_direction > 0.67:  # UP/FLAT
                    if height_cnt > 0:
                        bxs,spk,lva = self.flat_blocks(obstacle_pos[i], height_cnt)
                        self.pieces += [LevelPiece(obstacle_pos[i], bxs, spk, lva, height_cnt, height_cnt)]
                    else:
                        self.empty_platform()
                        self.pieces += [LevelPiece(obstacle_pos[i], [], [], [], height_cnt, height_cnt)]
                else:
                    if height_cnt > 0: #Off the floor
                        bxs,spk,lva = self.fall_down(obstacle_pos[i], height_cnt)
                        self.pieces += [LevelPiece(obstacle_pos[i], bxs, spk, lva, height_cnt, height_cnt-1)]
                        height_cnt -= 1
                    else:
                        self.empty_platform()
                        self.pieces += [LevelPiece(obstacle_pos[i], [], [], [], height_cnt, height_cnt)]
            height_cnt = max(0,height_cnt) #Make sure the height doesnt go below the floor
            height_cnt = min(self.max_height,height_cnt) #Make sure the height doesnt go beyond the height limit
            self.height_line += [height_cnt]
        self.height_line = self.get_height_line()

    def empty_platform(self):
        return

    def spikes_flat_1(self,pos,height):
        bxes = []
        spks = []
        lva = []
        spks.append(Spike((pos + BOX_SIZE,
                       self.ground_level - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))
        return bxes, spks, lva

    def spikes_flat_2(self,pos,height):
        bxes = []
        spks = [Spike((pos + BOX_SIZE,
                               self.ground_level - BOX_SIZE / 2 + 2 - BOX_SIZE * height)),Spike((pos + BOX_SIZE*2,
                               self.ground_level - BOX_SIZE / 2 + 2 - BOX_SIZE * height))]
        lva = []
        return bxes, spks, lva

    def spikes_flat_3(self,pos,height):
        bxes = []
        spks = [Spike((pos + BOX_SIZE,
                               self.ground_level - BOX_SIZE / 2 + 2 - BOX_SIZE * height)),Spike((pos + BOX_SIZE*2,
                               self.ground_level - BOX_SIZE / 2 + 2 - BOX_SIZE * height)),Spike((pos + BOX_SIZE*3,
                               self.ground_level - BOX_SIZE / 2 + 2 - BOX_SIZE * height))]
        lva = []
        return bxes, spks, lva

    def fall_down(self,pos,height):
        bxes = [Box((pos, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)),Box((pos + BOX_SIZE * 4,
                 self.ground_level - BOX_SIZE / 2 - BOX_SIZE * (height-1))),Box((pos + BOX_SIZE * 3,
                 self.ground_level - BOX_SIZE / 2 - BOX_SIZE * (height-1)))]
        spks = []
        lva = []
        if height > 1:
            for j in range(0, 5):
                lva.append(Lava((pos + BOX_SIZE * j, self.ground_level)))
        elif height > 0:
            for j in range(0, 3):
                lva.append(Lava((pos + BOX_SIZE * j, self.ground_level)))
        return bxes, spks, lva

    def jump_down(self,pos,height):
        bxes = []
        spks = []
        lva = []
        if height > 0: #Off the floor
            bxes.append(Box((pos, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
            if height == 1:
                for j in range(0, 4):
                    lva.append(Lava((pos + BOX_SIZE * j, self.ground_level)))
            else:
                for j in range(0, 5):
                    lva.append(Lava((pos + BOX_SIZE * j, self.ground_level)))
            bxes.append(Box(
                (pos + BOX_SIZE * 4, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * (height-1))))
        else: #One above floor, jump down to floor
            bxes.append(Box((pos, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
        return bxes, spks, lva

    def jump_up_1(self,pos,height):
        bxes = []
        spks = []
        lva = []
        if height > 0: #Off the floor
            bxes = [Box((pos, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)),Box((pos + BOX_SIZE * 4,
                     self.ground_level - BOX_SIZE / 2 - BOX_SIZE * (height + 1)))]
            lva = [Lava((pos + BOX_SIZE * 0, self.ground_level)),Lava((pos + BOX_SIZE * 1, self.ground_level)),Lava((pos + BOX_SIZE * 2, self.ground_level)),Lava((pos + BOX_SIZE * 3, self.ground_level)),Lava((pos + BOX_SIZE * 4, self.ground_level))]
        else:
            bxes = [Box((pos + BOX_SIZE * 4, self.ground_level - BOX_SIZE / 2 - BOX_SIZE))]
            lva = [Lava((pos + BOX_SIZE * 4, self.ground_level))]
            spks = [Spike((pos + BOX_SIZE*2,
                               self.ground_level - BOX_SIZE / 2 + 2 - BOX_SIZE * height)),Spike((pos + BOX_SIZE*3,
                               self.ground_level - BOX_SIZE / 2 + 2 - BOX_SIZE * height))]
        return bxes,spks,lva


    def jump_up_2(self,pos,height):
        bxes = []
        spks = []
        lva = []
        if height > 0: #Off the floor
            bxes.append(Box((pos, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))

            for j in range(0, 5):
                lva.append(Lava((pos + BOX_SIZE * j, self.ground_level)))

            bxes.append(
                Box((pos + BOX_SIZE * 4,
                     self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height - BOX_SIZE * 2)))
            bxes.append(
                Box((pos + BOX_SIZE * 3,
                     self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height - BOX_SIZE * 2)))
        else:
            bxes.append(Box((pos + BOX_SIZE * 4,
                     self.ground_level - BOX_SIZE / 2 - BOX_SIZE * 2)))
            lva.append(Lava((pos + BOX_SIZE * 4, self.ground_level)))
            spks = [Spike((pos + BOX_SIZE,
                           self.ground_level - BOX_SIZE / 2 + 2 - BOX_SIZE * height)), Spike((pos + BOX_SIZE * 2,
                                                                                              self.ground_level - BOX_SIZE / 2 + 2 - BOX_SIZE * height)),
                    Spike((pos + BOX_SIZE * 3,
                           self.ground_level - BOX_SIZE / 2 + 2 - BOX_SIZE * height))]

            self.spikes_flat_3(pos,height)
        return bxes, spks, lva

    def flat_blocks(self,pos,height):
        bxes = []
        spks = []
        lva = []
        for i in range(0,5):
            bxes.append(Box((pos + BOX_SIZE * i,
                            self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))

        if height > 0:
            for j in range(0, 5):
                lva.append(Lava((pos + BOX_SIZE * j, self.ground_level)))
        return bxes,spks,lva

    def flat_blocks_spike_1(self,pos,height):
        bxes = []
        spks = []
        lva = []
        if height > 0: #Off the floor
            for j in range(0, 5):
                bxes.append(Box((pos + BOX_SIZE * j,
                                    self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
            if height >= 1:
                for j in range(0, 5):
                    lva.append(Lava((pos + BOX_SIZE * j, self.ground_level)))

        spks.append(Spike((pos + BOX_SIZE + BOX_SIZE,
                   self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))
        return bxes, spks, lva

    def flat_blocks_spike_2(self,pos,height):
        bxes = []
        spks = []
        lva = []

        if height > 0: #Off the floor
            for j in range(0, 5):
                bxes.append(Box((pos + BOX_SIZE * j,
                                    self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
            if height >= 1:
                for j in range(0, 5):
                    lva.append(Lava((pos + BOX_SIZE * j, self.ground_level)))

        spks.append(Spike((pos + BOX_SIZE,
                   self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))

        spks.append(Spike((pos + BOX_SIZE*2,
                   self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))
        return bxes, spks, lva

    def flat_blocks_spike_3(self,pos,height):
        bxes = []
        spks = []
        lva = []

        if height > 0: #Off the floor
            for j in range(0, 5):
                bxes.append(Box((pos + BOX_SIZE * j,
                                    self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
            if height >= 1:
                for j in range(0, 5):
                    lva.append(Lava((pos + BOX_SIZE * j, self.ground_level)))

        spks.append(Spike((pos + BOX_SIZE,
                   self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))
        spks.append(Spike((pos + BOX_SIZE * 2,
                           self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))
        spks.append(Spike((pos + BOX_SIZE * 3,
                           self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))
        return bxes, spks, lva

    def flat_jump_lava(self,pos,height):
        bxes = []
        spks = []
        lva = []
        bxes.append(Box((pos, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
        bxes.append(Box((pos + BOX_SIZE * 4, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))

        lva.append(Lava((pos + BOX_SIZE, self.ground_level)))
        lva.append(Lava((pos + BOX_SIZE * 2, self.ground_level)))
        lva.append(Lava((pos + BOX_SIZE * 3, self.ground_level)))

        if height > 0:
            lva.append(Lava((pos, self.ground_level)))
            lva.append(Lava((pos + BOX_SIZE * 4, self.ground_level)))

        return bxes, spks, lva

    def get_all_obstacles(self, lower_bound, upper_bound):
        obstacles = pygame.sprite.Group()
        obstacles.add(self.platform)
        for b in self.boxes_objects:
            if lower_bound <= b.rect.topright[0] <= upper_bound:
                    obstacles.add(b)
        for s in self.spikes_objects:
            if lower_bound <= s.rect.topright[0] <= upper_bound:
                    obstacles.add(s)
        for s in self.lava_objects:
            if lower_bound <= s.rect.topright[0] <= upper_bound:
                    obstacles.add(s)
        return obstacles

    def get_spikes(self, lower_bound, upper_bound):
        obstacles = pygame.sprite.Group()
        for s in self.spikes_objects:
            if lower_bound <= s.rect.topright[0] <= upper_bound:
                    obstacles.add(s)
        return obstacles

    def get_lava(self, lower_bound, upper_bound):
        obstacles = pygame.sprite.Group()
        for s in self.lava_objects:
            if lower_bound <= s.rect.topright[0] <= upper_bound:
                    obstacles.add(s)
        return obstacles

    def get_boxes(self, lower_bound, upper_bound):
        obstacles = pygame.sprite.Group()
        obstacles.add(self.platform)
        for b in self.boxes_objects:
            if lower_bound <= b.rect.topright[0] <= upper_bound:
                    obstacles.add(b)
        return obstacles

    def get_all_spikes(self):
        obstacles = pygame.sprite.Group()
        for s in self.spikes_objects:
            obstacles.add(s)
        return obstacles

    def get_all_lava(self):
        obstacles = pygame.sprite.Group()
        for s in self.lava_objects:
            obstacles.add(s)
        return obstacles

    def get_all_boxes(self):
        obstacles = pygame.sprite.Group()
        for s in self.boxes_objects:
            obstacles.add(s)
        return obstacles

    def add_jump_flat(self, pos, height):
        if height == 0:
            for j in range(0, 5):
                self.boxes_objects.add(
                    Box((pos + BOX_SIZE * j, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
        if height > 0:
            for j in range(0, 5):
                self.boxes_objects.add(
                    Box((pos + BOX_SIZE * j, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
            for j in range(0, 5):
                self.lava_objects.add(Lava((pos + BOX_SIZE * j, self.ground_level)))
        return