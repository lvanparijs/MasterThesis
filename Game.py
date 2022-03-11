import copy
import csv
import random
import sys

import pygame
from pygame import font, KEYDOWN, K_SPACE, KEYUP, mixer

from os.path import exists

import pickle

from Box import Box
from Camera import Camera
from ComponentFrequencyCritic import ComponentFrequencyCritic
from EmptynessCritic import EmptynessCritic
from JumpCritic import JumpCritic
from Lava import Lava
from Level import Level, BOX_SIZE
from LevelPiece import LevelPiece
from LineCritic import LineCritic

# GLOBAL STUFF
from Song import Song
from SpeedCritic import SpeedCritic
from Spike import Spike
from VarietyCritic import VarietyCritic

vec = pygame.math.Vector2
ENTITY_SIZE = 40
FPS = 60
BG_COLOUR = (52, 157, 172)
NUM_PARTICLES = 150
LVL_W = 2000

ACC = 0.35
FRIC = -0.12
GRAVITY = 0.9
BUFFER = 5
JUMP_VEL = -14

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = (50, 50, 50)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)

font = "res/futureforces.ttf"


class Game(pygame.sprite.LayeredUpdates):

    def __init__(self, song_name, player, scr, scr_w, scr_h):
        # Display variables
        self.screen = scr
        self.screen_width = scr_w
        self.screen_height = scr_h

        # Game variables
        self.clock = pygame.time.Clock()  # Initialise game clock
        self.score = 0
        self.game_over = False

        self.is_jump = False  # Stores if player is jumping or not

        self.gradient = self.vertical_gradient((self.screen_width, self.screen_height), (1, 53, 61, 255),
                                               (52, 157, 172, 255))  # Nice background gradient
        # Update screen
        pygame.display.flip()

        self.player = player
        self.song_name = song_name
        self.level = None

        scr.blit(self.gradient, pygame.Rect((0, 0, scr_w, scr_h)))
        #self.no_gradient(scr,BG_COLOUR)
        pygame.display.update()
        self.game_loop()
        self.restart = self.game_over_screen()
        mixer.init()

    def game_over_screen(self):
        running = True
        lvl = Level(None, self.screen_height, self.player, [], self.screen_height * 0.9,[])
        text = self.text_format("GAME OVER", font, 100, white)
        text_menu = self.text_format("Press R to restart \t Press ESC for main menu", font, 20, white)

        alpha = 0
        d_alpha = 1
        while running:

            if alpha <= 0:
                d_alpha = 1
            elif alpha >= 255:
                d_alpha = -1
            alpha += d_alpha
            text.set_alpha(alpha)
            self.screen.blit(self.gradient, pygame.Rect((0, 0, self.screen_width, self.screen_height)))
            #self.no_gradient(self.screen,BG_COLOUR)
            self.screen.blit(text, (40, 250))
            self.screen.blit(text_menu, (60, 450))
            lvl.get_all_obstacles(0, self.screen_width).draw(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        mixer.music.stop()
                        running = False
                        return True
                    elif event.key == pygame.K_ESCAPE:
                        return False

            pygame.display.update()
            self.clock.tick(FPS)

    # Game Loop
    def game_loop(self):
        song_path = "res/"
        song_title = self.song_name # Load song0'
        extension = '.wav'
        song_name = song_path+song_title+extension
        mixer.music.load(song_name)
        self.screen.blit(self.gradient, pygame.Rect((0, 0, self.screen_width, self.screen_height)))  # Paint background
        #self.no_gradient(self.screen, BG_COLOUR)
        self.player.attempts += 1  # Increment Attempts

        self.total_level_height = self.screen_height * 4  # Set Max level height
        print("LOADING SONG")
        song = Song(song_name,False)
        lvl_path = "lvl/"
        filename = lvl_path+song_title+'.obj'

        if not exists(filename):
            num_levels = 10
            song = Song(song_name, True)
            print("GENERATING CANDIDATE LEVELS...")
            critics = [LineCritic(), VarietyCritic(), ComponentFrequencyCritic(), EmptynessCritic(), JumpCritic(), SpeedCritic()]

            l1 = self.evolve_levels(self.player, song, critics, 200, 20, 0.05, 50) #GA

            print("SAVING LEVEL...")

            with open(filename, 'wb') as filehandler:
                pickle.dump(l1.song,filehandler) #Need this to set the speed to desired level
                pickle.dump(self.player.gravity, filehandler) #Save gravity to recreate environment
                pickle.dump(l1.pieces, filehandler) #save all the level pieces

            filehandler.close()

        else:
            with open(filename, 'rb+') as f:
                song = pickle.load(f)
                player_grav = pickle.load(f)
                pieces = pickle.load(f)
                f.close()

                self.player.gravity = player_grav
                self.player.set_velocity(int((5 * BOX_SIZE) / song.spb))
                l1 = Level(song, self.total_level_height, self.player, pieces, self.screen_height,[])



        self.camera = Camera(self.complex_camera, l1.width, self.total_level_height)  # Initialise camera
        P1 = self.player
        jump = False
        last_jump = []
        jump_adjust_x = 0
        jump_adjust_y = 0
        num_pts = 35
        old_pos_y = 0


        start_time = 0
        countdown = True
        music_on = False
        while not self.game_over:  # Game over check
            cam_rect = self.camera.apply(P1.rect)  # Move camera with player
            start_time += 1 / FPS  # Increment timer

            # Manual jump
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        jump = True
                        last_jump = []
                        jump_adjust_x = 0
                        jump_adjust_y = 0
                        old_pos_y = self.camera.state.y
                        for i in range(0, num_pts):
                            last_jump += [vec(cam_rect.centerx, cam_rect.bottom) + P1.sim_jump(i)]
                if event.type == KEYUP:
                    if event.key == K_SPACE:
                        jump = False

            if jump:
                P1.jump(l1.boxes_objects)
                jump = False

            old_pos_x = P1.pos.x  # Change position

            # Update player without checking for collisions
            P1.move(l1.width)

            self.game_over = P1.update(l1)  # Update player and collisions
            if self.game_over:
                self.explosion(P1, l1)  # Animation

            # Update Camera
            self.camera.update(P1)
            jump_adjust_x += P1.pos.x - old_pos_x
            jump_adjust_y = old_pos_y - self.camera.state.y

            # Draw updates screen
            self.screen.blit(self.gradient, pygame.Rect((0, 0, self.screen_width, self.screen_height)))
            #self.no_gradient(self.screen, BG_COLOUR)

            #Draw Platform, finish and pieces
            self.draw_platform(l1.get_platform())
            self.draw_finish_flag(l1.finish_flag)
            self.draw(l1.get_pieces_in_range(P1.pos.x - self.screen_width,P1.pos.x + self.screen_width))

            # DRAW SCORE
            #if not countdown:
            #    text = self.text_format("ATTEMPT " + str(P1.get_attempts()), font, 60, white)
            #    self.screen.blit(text, (40, 400))

            P1.draw(self.screen, self.camera)  # Draw player
            pygame.display.update()  # Update
            self.clock.tick(FPS)  # Increment clock

            if countdown:
                mixer.music.unload()
                mixer.music.load('res/countdown.wav')
                mixer.music.set_endevent(pygame.ACTIVEEVENT)
                mixer.music.play()
                while mixer.music.get_busy():
                    continue
                mixer.music.stop()
                mixer.music.unload()
                mixer.music.load(song_name)
                countdown = False
            elif not music_on and P1.pos[0] >= l1.start_buffer:
                mixer.music.play()  # Play music
                music_on = True

    def draw_platform(self,platform):
        self.screen.blit(platform.surf, self.camera.apply(platform.rect))

    def draw_finish_flag(self,pos):
        surf = pygame.image.load("res/flag.png").convert_alpha()  # Get sprite for player
        rect = surf.get_rect(bottomleft=pos)
        self.screen.blit(surf,self.camera.apply(rect))

    def draw(self, pieces):
        for p in pieces:
            for b in p.boxes: #b is the position of the box
                bx = Box(b)
                self.screen.blit(bx.surf, self.camera.apply(bx.rect))
            for s in p.spikes: #b is the position of the box
                sp = Spike(s)
                self.screen.blit(sp.surf, self.camera.apply(sp.rect))
            for l in p.lava: #b is the position of the box
                lv = Lava(l)
                self.screen.blit(lv.surf, self.camera.apply(lv.rect))

    def mini_explosion(self, prtcles):
        if len(prtcles) > 0:
            for p in prtcles:  # Particle check
                if p.get_alpha() <= 0:
                    prtcles.remove(p)
                else:
                    p.update()
                    p.draw(self.screen, self.camera)
            return False
        else:
            return True

    def explosion(self, player, lvl):
        pos = player.rect.center
        # Explosion animation, purely for aesthetics
        #particles = []
        #for i in range(1, NUM_PARTICLES):
        #    particles += [Particle(pos)]

        circle_size = 5
        circle_alpha = 180

        while circle_alpha > 0:  # Run until all particles faded

            self.screen.blit(self.gradient, pygame.Rect((0, 0, self.screen_width, self.screen_height)))
            #self.no_gradient(self.screen, BG_COLOUR)
            self.draw_platform(lvl.get_platform())
            self.draw(lvl.get_pieces_in_range(self.camera.state.topleft[0], self.camera.state.topright[0]))
            circle_size += 2
            circle = pygame.Surface((circle_size * 2, circle_size * 2), pygame.SRCALPHA)
            circle_alpha -= 5
            circle_alpha = max(0, circle_alpha)
            pygame.draw.circle(circle, (255, 255, 0, circle_alpha), (circle_size, circle_size), circle_size)

            self.screen.blit(circle, self.camera.apply(circle.get_rect(center=pos)))

            #for p in particles:  # Particle check
            #    if p.get_alpha() <= 0:
            #        particles.remove(p)
            #    else:
            #        p.update()
            #        p.draw(self.screen, self.camera)
            pygame.display.update()
            self.clock.tick(FPS)

    def generate_rhythm(self, song):
        NO_ACTION = 0
        JUMP = 1
        al = []
        flat_cnt = 2
        for b in song.beat_times: #Generates actions for the times of the beats
            if flat_cnt > 0:
                al += [NO_ACTION]
                flat_cnt-=1
            elif random.uniform(0,1) > random.uniform(0,1):
                al += [NO_ACTION]
            else:
                al += [JUMP]
        return al

    def evolve_levels(self, player, song, critics, population_size, reproduction_size, mutation_rate, num_generations):
        al = self.generate_rhythm(song) #Generate Rhythm for all the levels
        fitness_over_generations = []
        levels = []
        for i in range(0, population_size): #Generate initial population
            levels += [Level(song, self.total_level_height, player, [], self.screen_height,al)]
            levels[i].generate_geometry_from_grammar_rnd(player.max_vel)

        print("++++++++++++++++++++++")
        best_level = levels[0]
        old_avg = 0
        for g in range(0, num_generations):
            print("+++++++++++++++++++++++++++++++++++")
            print("GENERATION: "+str(g))
            print("CRITIQUING LEVELS...")
            lvl_scores = []
            for lvl in levels:
                lvl_scores += [0]
                for c in critics:
                    c.print()
                    scr = c.critique(lvl)
                    lvl_scores[-1] += scr
            avg = sum(lvl_scores)/len(lvl_scores)
            print("AVERAGE SCORE: "+str(avg))
            print("OLD AVERAGE: "+str(old_avg))
            print("IMPROVED WITH: "+str(avg-old_avg))
            old_avg = avg
            fitness_over_generations += [[avg,g]]
            print("+++++++++++++++++++++++++++++++++++")
            print("CHOOSING BEST LEVELS...")

            best_old_gen = []
            new_levels = []
            for i in range(0, reproduction_size):
                best_idx = lvl_scores.index(max(lvl_scores))
                lvl_scores.pop(best_idx)
                best_old_gen += [levels.pop(best_idx)]  # add to next generation population
                if i == 0:
                    best_level = best_old_gen[-1]

            # Mutation and crossover
            for p in range(len(best_old_gen), population_size):
                #Choose parents
                parent1 = best_old_gen[random.randint(1, len(best_old_gen) - 1)]
                parent2 = best_old_gen[random.randint(1, len(best_old_gen) - 1)]  # Choose second parent randomly from the best of the previous generation
                while parent2 == parent1:  # Try again if its the same level
                    parent2 = best_old_gen[random.randint(1, len(best_old_gen) - 1)]  # Choose second parent randomly

                # Pick random spot to cut, one point crossover
                cut_off = random.randint(0, len(parent1.get_pieces()))

                parent_pieces1 = copy.deepcopy(parent1.get_pieces())
                parent_pieces2 = copy.deepcopy(parent2.get_pieces())

                if len(parent_pieces1) == 0 or len(parent_pieces2) == 0: #In case one parent is empty, return the other
                    if len(parent_pieces1) == 0:
                        new_levels += parent2
                    else:
                        new_levels += parent1
                else:
                    child1 = parent_pieces1[:cut_off] + parent_pieces2[cut_off:] #Crossover
                    #child2 = parent_pieces2[:cut_off] + parent_pieces1[cut_off-1:-1]

                    #Smooth out the new child, the cutoff can produce unfeasible results
                    final1 = self.interpolate(parent1, child1)

                    if random.uniform(0,1) < mutation_rate: #mutate individual
                        mutation_id = random.randint(1,len(final1)-1)
                        final1[mutation_id] = parent1.choose_level_piece(final1[mutation_id].pos, final1[mutation_id].start_height,
                                                       final1[mutation_id].end_height) #Choose a random piece to replace it

                    #Add child 1 to next population
                    new_levels += [Level(parent1.song, parent1.height, player, final1, self.screen_height, al)]
            new_levels.extend(best_old_gen) #Add best from previous generation and do it again
            levels = new_levels

        fields = ['Fitness', 'Generation']

        with open(song.file_name+'Evolution.csv', 'w') as f:
            # using csv.writer method from CSV package
            write = csv.writer(f)
            write.writerow(fields)
            write.writerows(fitness_over_generations)
        print("START HEIGHT OF BEST LEVEL:")
        print(best_level.pieces[0].start_height)
        return best_level


    def interpolate(self,lvl,pieces):
        start_pieces = copy.deepcopy(pieces)
        new_pieces = copy.deepcopy(pieces)
        for i in range(0,len(new_pieces)):
            height_diff = new_pieces[i-1].end_height-new_pieces[i].start_height #Calculate difference between pieces
            if abs(height_diff) > 0: #If difference is 1 or less these pieces are legal
                #need to interpolate/smoothe out the level, choose new piece to replace this one
                if height_diff < 0: #Second piece is too high
                    new_pieces[i] = lvl.choose_level_piece(new_pieces[i].pos, new_pieces[i - 1].end_height,
                                                       new_pieces[i - 1].end_height + 1)
                else: #Second piece too low
                    new_pieces[i] = lvl.choose_level_piece(new_pieces[i].pos, new_pieces[i - 1].end_height,
                                                       new_pieces[i - 1].end_height - 1)

        new_pieces[0] = LevelPiece(new_pieces[0].pos, [], [], [], 0, 0) #Enforce empty platform as first piece to give the player soe time to react
        #DEBUGGING STUFF :) DOESNT DO ANYTHING TO THE FINAL RESULT
        #final_pieces = []
        #height_map_new = []
        #height_map_old = []
        #different = False
        #for i in range(0,len(new_pieces)):
        #    #Generate replacement pieces
        #    if i == 0:
        #        final_pieces = [LevelPiece(new_pieces[i].pos,[],[],[],0,0)] #Enforce first piece flat
        #    else:
        #        final_pieces += [lvl.choose_level_piece(new_pieces[i].pos, final_pieces[i-1].end_height,
        #                                               new_pieces[i].end_height)]
        #    height_map_old += [(start_pieces[i].start_height,start_pieces[i].end_height)]
        #    height_map_new += [(new_pieces[i].start_height, new_pieces[i].end_height)]
        #    if start_pieces[i].start_height != new_pieces[i].start_height or start_pieces[i].end_height != new_pieces[i].end_height:
        #        different = True

        #print("+++++++++++++++++++++++++++++++++++++++")
        #if different:
        #    print("CHANGE IN PIECES LISTS")
        #    print("OLD")
        #    print(height_map_old)
        #    print("NEW")
        #    print(height_map_new)
        #else:
        #    print("NO CHANGE IN PIECES LISTS")
        #    print("OLD")
        #    print(height_map_old)
        #print("+++++++++++++++++++++++++++++++++++++++")
        return new_pieces

    def simple_camera(self, camera, target_rect):
        l, t, _, _ = target_rect  # l = left,  t = top
        _, _, w, h = camera  # w = width, h = height
        return pygame.Rect(-l + self.screen_width / 6, -t + self.screen_height / 2, w, h)

    def complex_camera(self, camera, target_rect):
        # we want to center target_rect
        x = -target_rect.center[0] + self.screen_width / 6
        y = -target_rect.center[1] + self.screen_height / 2
        # move the camera. Let's use some vectors so we can easily substract/multiply
        camera.topleft += (pygame.Vector2((x, y)) - pygame.Vector2(
            camera.topleft)) * 0.06  # add some smoothness coolnes
        # set max/min x/y so we don't see stuff outside the world
        camera.x = max(-(camera.width - self.screen_width), min(0, camera.x))
        camera.y = max(-(camera.height - self.screen_height), min(0, camera.y))

        return camera

    # Text Renderer
    def text_format(self, message, textFont, textSize, textColor):
        newFont = pygame.font.Font(textFont, textSize)
        newText = newFont.render(message, True, textColor)
        return newText

    def no_gradient(self,screen,color):
        screen.fill(color)

    def vertical_gradient(self, size, startcolor, endcolor):
        """
        Draws a vertical linear gradient filling the entire surface. Returns a
        surface filled with the gradient (numeric is only 2-3 times faster).
        """
        height = size[1]
        bigSurf = pygame.Surface((1, height)).convert_alpha()
        dd = 1.0 / height
        sr, sg, sb, sa = startcolor
        er, eg, eb, ea = endcolor
        rm = (er - sr) * dd
        gm = (eg - sg) * dd
        bm = (eb - sb) * dd
        am = (ea - sa) * dd
        for y in range(height):
            bigSurf.set_at((0, y),
                           (int(sr + rm * y),
                            int(sg + gm * y),
                            int(sb + bm * y),
                            int(sa + am * y))
                           )
        return pygame.transform.scale(bigSurf, size)

    #def aaline(self, surface, color, start_pos, end_pos, width=1):
    #    """ Draws wide transparent anti-aliased lines. """
    #    # ref https://stackoverflow.com/a/30599392/355230#

    #    x0, y0 = start_pos
    #    x1, y1 = end_pos
    #    midpnt_x, midpnt_y = (x0 + x1) / 2, (y0 + y1) / 2  # Center of line segment.
    #    length = math.hypot(x1 - x0, y1 - y0)
    #    angle = math.atan2(y0 - y1, x0 - x1)  # Slope of line.
    #    width2, length2 = width / 2, length / 2
    #    sin_ang, cos_ang = math.sin(angle), cos(angle)

    #    width2_sin_ang = width2 * sin_ang
    #    width2_cos_ang = width2 * cos_ang
    #    length2_sin_ang = length2 * sin_ang
    #    length2_cos_ang = length2 * cos_ang

    #    # Calculate box ends.
    #    ul = (midpnt_x + length2_cos_ang - width2_sin_ang,
    #          midpnt_y + width2_cos_ang + length2_sin_ang)
    #    ur = (midpnt_x - length2_cos_ang - width2_sin_ang,
    #          midpnt_y + width2_cos_ang - length2_sin_ang)
    #    bl = (midpnt_x + length2_cos_ang + width2_sin_ang,
    #          midpnt_y - width2_cos_ang + length2_sin_ang)
    #    br = (midpnt_x - length2_cos_ang + width2_sin_ang,
    #          midpnt_y - width2_cos_ang - length2_sin_ang)

    #    pygame.gfxdraw.aapolygon(surface, (ul, ur, br, bl), color)
    #    pygame.gfxdraw.filled_polygon(surface, (ul, ur, br, bl), color)
