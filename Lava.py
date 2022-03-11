import pygame

class Lava(pygame.sprite.Sprite):

    def __init__(self, pos):
        super().__init__()
        self.surf = pygame.Surface((40, 20))
        self.surf.fill((0, 0, 0))
        self.rect = self.surf.get_rect(center=pos)
        self.pos = pos
        self.image = self.surf
        self.mask = pygame.mask.from_surface(self.image)