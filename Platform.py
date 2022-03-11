import pygame


class Platform(pygame.sprite.Sprite):
    def __init__(self, pos, lvl_width):
        super().__init__()
        self.surf = pygame.Surface((lvl_width, 5))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(topleft = pos)
        self.image = self.surf
        self.mask = pygame.mask.from_surface(self.image)


    def draw(self,surface):
        pygame.draw.rect(surface, (255,255,255), self.rect,2)
