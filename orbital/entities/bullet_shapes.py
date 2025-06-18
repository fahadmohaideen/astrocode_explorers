import pygame
pygame.init()

class Circle:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.shape = "circle"

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class Square:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.shape = "square"

    def draw(self, surface):
        top_left_x = self.x - self.size // 2
        top_left_y = self.y - self.size // 2
        pygame.draw.rect(surface, self.color, (top_left_x, top_left_y, self.size, self.size))
class Triangle:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.shape = "triangle"
        self.points_relative = [
            (0, -size / 2),
            (-size / 2, size / 2),
            (size / 2, size / 2)
        ]

    def draw(self, surface):
        translated_points = [(self.x + p[0], self.y + p[1]) for p in self.points_relative]
        pygame.draw.polygon(surface, self.color, translated_points)