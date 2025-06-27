# Circle, Square, Triangle classes
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

# --- Square Class ---
class Square:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.shape = "square"

    def draw(self, surface):
        # The rect should be centered around self.x, self.y
        top_left_x = self.x - self.size // 2
        top_left_y = self.y - self.size // 2
        pygame.draw.rect(surface, self.color, (top_left_x, top_left_y, self.size, self.size))

# --- Triangle Class ---
class Triangle:
    def __init__(self, x, y, size, color): # Assuming 'size' helps determine dimensions
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.shape = "triangle"
        # Define vertices relative to (0,0) and then translate
        # Example: equilateral triangle pointing up
        # You might need to adjust these points based on how you want your triangle oriented
        self.points_relative = [
            (0, -size / 2),
            (-size / 2, size / 2),
            (size / 2, size / 2)
        ]

    def draw(self, surface):
        # Translate the relative points to the current (self.x, self.y)
        translated_points = [(self.x + p[0], self.y + p[1]) for p in self.points_relative]
        pygame.draw.polygon(surface, self.color, translated_points)