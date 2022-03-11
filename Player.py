import copy
import math
import numpy as np
import pygame

vec = pygame.math.Vector2
ACC = 0.35
FRIC = -0.12
FPS = 60
TIMESTEP = 1 / FPS
GRAVITY = 0.8
BUFFER = 10
JUMP_VEL = -15
BLOCK_SIZE = 40


class Player(pygame.sprite.Sprite):

    def __init__(self, pos):
        super().__init__()
        self.surf = pygame.image.load("res/player.png").convert_alpha()  # Get sprite for player
        self.rect = self.surf.get_rect()
        self.image = self.surf
        self.mask = pygame.mask.from_surface(self.image)
        self.gravity = GRAVITY
        self.start_pos = vec(pos)
        self.pos = vec(pos)  # Starting position in m
        self.vel = vec(0, 0)  # Velocity in m/s
        self.acc = vec(ACC, self.gravity)  # Acceleration in m/s^2
        self.pixels_per_second = 450

        self.rotate = False  # Rotation boolean, triggers animation
        self.angle = 0  # Angle, for animation purposes
        self.ang_vel = math.pi / 20  # Angular displacement per timestep in radians
        self.max_vel = 5
        self.attempts = 0
        self.cnt = 0
        self.old_pos = 0

        self.desired_vel = 0

    def reset(self, pos):
        self.pos = vec(pos)
        self.vel = vec(0, 0)  # Velocity
        self.acc = vec(ACC, self.gravity)  # Acceleration

    def get_attempts(self):
        return self.attempts

    def move(self, width):
        self.acc = vec(0, self.gravity)  # Constant velocity in x, but gravity still applies
        self.vel.y += self.acc.y  # gravity
        self.vel.x = self.max_vel  # CONSTANT VELOCITY
        self.pos += (self.vel + 0.5 * self.acc)  # update pos
        if self.pos.x > width:  # Check if player is outside of Level
            self.pos.x = 0
        self.rect.midbottom = self.pos

    def box_collision_check(self, entities):
        for e in entities:
            if self.rect.colliderect(e):
                # Top collision
                if self.rect.bottom >= e.rect.top and self.rect.bottomright[0] >= e.rect.bottomleft[0]:
                    self.vel.y = 0
                    self.pos.y = e.rect.top+1 #+1 is to solve the jittering when the player is moving on a flat surface
                    self.rotate = False
                    self.angle = 0
                # Side collision
                if self.rect.bottomright[0] >= e.rect.bottomleft[0] and self.rect.centery > e.rect.top:
                    return True  # Collision, game over
        return False

    def update(self, lvl):
        game_over = False
        hits_spike = pygame.sprite.spritecollide(self, lvl.get_spikes(self.pos[0],self.pos[0]+BLOCK_SIZE*5), False, pygame.sprite.collide_mask)
        hits_lava = pygame.sprite.spritecollide(self, lvl.get_lava(self.pos[0],self.pos[0]+BLOCK_SIZE*5), False, pygame.sprite.collide_mask)

        if self.pos[0] >= lvl.finish_flag[0]:
            game_over = True
        if hits_spike or hits_lava:
            game_over = True
        collision_type = self.box_collision_check(lvl.get_all_boxes())
        if collision_type:
            game_over = True

        if self.rotate:
            self.angle += self.ang_vel
            if abs(self.angle) >= 2 * math.pi:
                self.angle = 0
        return game_over

    def jump(self, entities):
        hits = pygame.sprite.spritecollide(self, entities, False)
        if hits:
            self.vel.y = JUMP_VEL
            self.rotate = True

    def normalise(self, v):
        return v / np.sqrt(np.sum(v * v))

    def get_jump_length(self):
        _, y_start = self.sim_jump(1)
        for i in range(2, 50):
            _, y = self.sim_jump(i)
            if y >= y_start:
                return i  # Jump complete

    def sim_jump(self, t):
        return (vec(self.max_vel, JUMP_VEL) * t) + 0.5 * vec(0, GRAVITY) * (t * t)

    def sim_no_jump(self, t):
        return vec(t * self.max_vel, 0) + 0.5 * vec(0, GRAVITY) * (t * t)

    def sim_jump_with_params(self, t, v, j_v, g):
        return (vec(v, j_v) * t) + 0.5 * vec(0, g) * (t * t)

    def set_velocity(self, pps):
        self.max_vel = (pps / FPS)

    def projectile_xy(self, t):
        '''
        calculate a list of (x, y) projectile motion data points
        where:
        x axis is distance (or range) in meters
        y axis is height in meters
        v is muzzle velocity of the projectile (meter/second)
        a is the firing angle with repsect to ground (radians)
        hs is starting height with respect to ground (meters)
        g is the gravitational pull (meters/second_square)
        '''
        data_xy = []
        v = self.vel * 6

        a = math.atan2(v.x, v.y) * 6

        # now calculate the height y
        y = (t * v.y * math.sin(a)) - (GRAVITY * t * t) / 2
        # calculate the distance x
        x = v.x * math.cos(a) * t
        return (int(x), int(y))

    def simulate_jump(self, width, entities):
        tmp_player = Player(copy.deepcopy(self.pos))
        tmp_player.vel = copy.deepcopy(self.vel)  # Velocity
        tmp_player.acc = vec(ACC, self.gravity)  # Acceleration
        tmp_player.jump(entities)

        pts = [copy.deepcopy(tmp_player.pos)]

        for i in range(0, FPS):  # Simulate0.5 second ahead
            tmp_player.move(width)
            tmp_player.update(entities)
            if len(pts) < 2:
                pts += [copy.deepcopy(tmp_player.pos)]
            else:
                if pts[len(pts) - 1].y != pts[len(pts) - 2].y:
                    if i % 3 == 0:
                        pts += [copy.deepcopy(tmp_player.pos)]

        return pts

    def draw(self, surface, camera):
        cam_rect = camera.apply(self.rect)
        if self.angle:
            rot_img, new_rect = self.blitRotateCenter(surface, self.image, self.rect.topleft, self.angle)
            surface.blit(rot_img, camera.apply(new_rect))
        else:
            surface.blit(self.image, cam_rect)

    def blitRotateCenter(self, surf, image, topleft, angle):
        rotated_image = pygame.transform.rotate(image, math.degrees(-angle))
        new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)
        return rotated_image, new_rect

    def parameter_tuning(self, error):
        max_g = 2
        min_g = 0.1
        increment = 0.01

        g_range = [min_g,max_g]
        g_costs = [10,10]
        while (sum(g_costs)/2) > error:
            if g_costs[0] < g_costs[1]:
                g_range = [g_range[0], g_range[1]-increment]
            elif g_costs[0] > g_costs[1]:
                g_range = [g_range[0]+increment, g_range[1]]
            elif g_range[0] > g_range[1]: #Cross
                self.gravity = sum(g_range) / 2
                return

            for j in range(0,len(g_range)):
                pts = []
                i = 1
                pts += [self.sim_jump_with_params(i, self.max_vel, JUMP_VEL, g_range[j])]
                while pts[-1][1] < 0:
                    pts += [self.sim_jump_with_params(i, self.max_vel, JUMP_VEL, g_range[j])]
                    i += 1

                g_costs[j] = abs((pts[-1][0] - 5 * BLOCK_SIZE))#Distance from desired jump distance


        self.gravity = sum(g_range)/2



