import math
import time

import pygame
from pygame.math import Vector3 as vec3

pygame.init()
screen = pygame.display.set_mode((1280, 720))

all_points = pygame.sprite.LayeredUpdates()

# ---------- Constants ---------- #
W = 1280
H = 720

RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (255, 0, 254)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class PointBase(pygame.sprite.Sprite):
    def __init__(self, x, y, z, size=32):
        super().__init__()
        self.size = size
        self.true_size = size
        self.pos = vec3(x, y, z)

    def scale_to_depth(self) -> None:
        try:
            self.size = self.true_size * (0.5 * W / self.pos.z)
        except ZeroDivisionError:
            self.size = 1280
        all_points.change_layer(self, 1280 - self.pos.z)  # noqa


class CenterOfMass(pygame.sprite.Sprite):
    def __init__(self, x, y, z, size=32):
        super().__init__()
        self.layer = 1
        all_points.add(self)  # noqa

        self.verts = []  # noqa

        self.true_size = size
        self.size = size
        self.pos = vec3(x, y, z)
        self.angle = [0, 0, 0]

        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
        self.image = pygame.Surface((size, size))

    def rotate(self, x_rate, y_rate, z_rate) -> None:
        """Rotates the object and its children along any of its 3 axes of rotation

        :param x_rate: The rate to rotate the object along the x-axis
        :param y_rate: The rate to rotate the object along the y-axis
        :param z_rate: The rate to rotate the object along the z-axis
        :return: None
        """
        vert: vec3
        for vert in self.verts:
            new_pos: vec3 = vert.pos_offset.copy()
            new_pos.rotate_x_ip(self.angle[0])
            new_pos.rotate_y_ip(self.angle[1])
            new_pos.rotate_z_ip(self.angle[2])
            vert.pos = self.pos + new_pos * (0.5 * W / self.pos.z)  # Multiplier potentially incorrect

        self.angle[0] += x_rate
        self.angle[1] += y_rate
        self.angle[2] += z_rate

    def generate_mesh(self):
        for vert1 in self.verts:
            for vert2 in [v for v in self.verts if v is not vert1]:
                pygame.draw.aaline(screen, BLACK, (vert1.pos.x, vert1.pos.y), (vert2.pos.x, vert2.pos.y))

    def update(self):
        # Adjusting size for depth illusion
        try:
            self.size = self.true_size * (0.5 * W / self.pos.z)
        except ZeroDivisionError:
            self.size = 1280

        self.image = pygame.Surface((self.size, self.size))
        self.image.fill((255, 0, 255))
        pygame.draw.circle(self.image, (255, 0, 0),
                           (self.image.get_width() // 2, self.image.get_height() // 2), self.size // 2)
        self.image.set_colorkey((255, 0, 255))

        self.rect = self.image.get_rect()
        self.rect.center = (self.pos.x, self.pos.y)

        all_points.change_layer(self, 1280 - self.pos.z)  # noqa

        self.generate_mesh()

        self.pos.x = W / 2 + math.cos(time.time()) * W / 4
        self.pos.z = W / 2 + math.cos(time.time()) * W / 4
        self.pos.y = H / 2 + math.sin(time.time()) * H / 6


class Vertex(pygame.sprite.Sprite):
    def __init__(self, com: CenterOfMass, x, y, z, size=64, color=BLACK):
        super().__init__()
        self.layer = 2
        all_points.add(self)  # noqa

        self.parent = com

        self.true_size = size
        self.size = size
        self.pos = vec3(com.pos.x + x, com.pos.y + y, com.pos.z + z)
        self.pos_offset = vec3(x, y, z)

        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
        self.image = pygame.Surface((16, 16))
        self.color = color

    def update(self):
        # Adjusting size for depth illusion
        try:
            self.size = self.true_size * (0.5 * W / self.pos.z)
        except ZeroDivisionError:
            self.size = 1280

        self.image = pygame.Surface((self.size, self.size))
        self.image.fill((255, 0, 255, 0))
        pygame.draw.circle(self.image, self.color,
                           (self.image.get_width() // 2, self.image.get_height() // 2), self.size // 2)
        self.image.set_colorkey((255, 0, 255))

        self.rect = self.image.get_rect()
        self.rect.center = (self.pos.x, self.pos.y)

        all_points.change_layer(self, 1280 - self.pos.z)  # noqa


def main():
    com = CenterOfMass(W/2, H/2, W/2)

    com.verts.append(Vertex(com, 64, 64, 64, 32, GREEN))
    com.verts.append(Vertex(com, -64, -64, 64, 32, GREEN))
    com.verts.append(Vertex(com, 64, -64, 64, 32, BLUE))
    com.verts.append(Vertex(com, -64, 64, 64, 32, BLUE))

    com.verts.append(Vertex(com, 64, 64, -64, 32, PURPLE))
    com.verts.append(Vertex(com, -64, -64, -64, 32, PURPLE))
    com.verts.append(Vertex(com, 64, -64, -64, 32, YELLOW))
    com.verts.append(Vertex(com, -64, 64, -64, 32, YELLOW))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        com.rotate(0.1, 0.1, 0)

        screen.fill((255, 255, 255))

        all_points.update()
        all_points.draw(screen)

        pygame.display.flip()


if __name__ == '__main__':
    main()