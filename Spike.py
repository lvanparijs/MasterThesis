import pygame

class Spike(pygame.sprite.Sprite):

    def __init__(self, pos):
        super().__init__()
        self.surf = pygame.image.load("res/spike.png").convert_alpha()
        self.rect = self.surf.get_rect(center=pos)
        self.pos = pos
        self.image = self.surf
        self.mask = pygame.mask.from_surface(self.image)

