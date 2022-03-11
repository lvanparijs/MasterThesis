import pygame


class Box(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.surf = pygame.image.load("res/block.png").convert_alpha()
        self.rect = self.surf.get_rect(center=pos)
        self.pos = pos
        self.image = self.surf
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self,surface):
        pygame.draw.rect(surface, (0, 0, 0), self.rect)
        pygame.draw.rect(surface, (255,255,255), self.rect,2)

    def gen_temp_block(self,pos):
        surf = pygame.image.load("res/block.png").convert_alpha()
        rect = surf.get_rect(center=pos)
        return rect