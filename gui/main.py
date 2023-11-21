import pygame
import numpy as np
from pygame.locals import *

bg_color = (255, 255, 255)
black = (0, 0, 0)
white = (255, 255, 255)

window_width = 500
window_height = 500
board_width = 500
grid_size = 30

board_size = 15
empty = 0
black_stone = 1
white_stone = 2

fps = 60
fps_clock = pygame.time.Clock()

def main():
    pygame.init()
    surface = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Omok-HI")
    surface.fill(bg_color)

    omok = Omok(surface)
    while True:
        run_game(surface, omok)

def run_game(surface, omok):
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == MOUSEBUTTONUP:
                omok.check_board(event.pos)

        pygame.display.update()
        fps_clock.tick(fps)

class Omok(object):
    def __init__(self, surface):
        self.board = np.zeros((board_size, board_size))
        self.surface = surface
        self.pixel_coords = []
        self.set_coords()
        self.set_image()

        self.turn = black_stone
        self.draw_board()
        self.coords = []

    def set_image(self):
        black_img = pygame.image.load('image/black.png')
        white_img = pygame.image.load('image/white.png')
        self.board_img = pygame.image.load('image/board.png')
        self.black_img = pygame.transform.scale(black_img, (grid_size, grid_size))
        self.white_img = pygame.transform.scale(white_img, (grid_size, grid_size))

    def draw_board(self):
        self.surface.blit(self.board_img, (0, 0))

    def draw_images(self):
        img = [self.black_img, self.white_img]
        for i in range(len(self.coords)):
            x, y = self.coords[i]
            self.surface.blit(img[i % 2], (x, y))

    def draw_stone(self, coord, stone):
        x, y = self.get_point(coord)
        self.board[y][x] = stone
        self.draw_images()
        self.turn = 3 - self.turn

    def set_coords(self):
        for y in range(board_size):
            for x in range(board_size):
                self.pixel_coords.append((x * grid_size + 25, y * grid_size + 25))

    def get_coord(self, pos):
        for coord in self.pixel_coords:
            x, y = coord
            rect = pygame.Rect(x, y, grid_size, grid_size)
            if rect.collidepoint(pos):
                return coord
        return None

    def get_point(self, coord):
        x, y = coord
        x = (x - 25) // grid_size
        y = (y - 25) // grid_size
        return x, y

    def check_board(self, pos):
        coord = self.get_coord(pos)
        if not coord:
            return False
        x, y = self.get_point(coord)
        if self.board[y][x] != empty:
            return True

        self.coords.append(coord)
        self.draw_stone(coord, self.turn)
        return True


main()
