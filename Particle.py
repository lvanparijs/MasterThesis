import random
from random import randint

import pygame
vec = pygame.math.Vector2
FRIC = -0.12
GRAVITY = 0.03

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.surf = pygame.Surface((randint(8,12), randint(8,12)))
        self.colour = (randint(230, 255), randint(100, 155), randint(0, 30))
        self.surf.fill(self.colour)
        self.rect = self.surf.get_rect(center=pos)
        self.image = self.surf
        self.pos = pos

        self.angle = randint(0,359)
        self.vel = vec(random.uniform(-1,1), random.uniform(-1,1))
        self.acc = vec(random.uniform(-0.5,0.5), random.uniform(-1,0.5))
        self.alpha = randint(100,255)
        self.surf.set_alpha(self.alpha)
        self.alpha_increment = 4

    def update(self):
        self.acc += vec(0,GRAVITY)
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        self.rect = self.surf.get_rect(center=self.pos)

    def draw(self,surface,camera):
        self.alpha = self.alpha - self.alpha_increment
        self.surf.set_alpha(self.alpha)
        surface.blit(self.surf, camera.apply(self.rect))

    def get_alpha(self):
        return self.alpha
