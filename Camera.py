import pygame


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = pygame.Rect(0, 0, width, height)
        self.width = width  # Level width
        self.height = height  # Level height

    def apply(self, target):
        return target.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)
