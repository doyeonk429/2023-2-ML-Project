import sys
import threading
import time

import pygame
import numpy as np
from pygame.locals import *

import shared
from node import Node

bg_color = (255, 255, 255)
black = (0, 0, 0)
white = (255, 255, 255)

window_width = 500
window_height = 500
board_width = 500
grid_size = 30

board_size = 15
empty = 0
black_stone = shared.BLACK
white_stone = shared.WHITE

fps = 60
fps_clock = pygame.time.Clock()




def main(player_stone: int):
    pygame.init()
    surface = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Omok-HI")
    surface.fill(bg_color)

    omok = Omok(surface,player_stone)
    # selectLevel = # hard 면 true, easy면 false
    t = threading.Thread(target=start_ai_thread,args=(omok,selectLevel,))
    t.daemon = True
    t.start()
    while True:
        run_game(surface, omok)




game_over = False
def run_game(surface, omok):
    global game_over
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == MOUSEBUTTONUP:
                if game_over:
                    continue
                if not omok.is_player_turn():
                    message_box("플레이어 차례가 아닙니다")
                    continue
                coord = omok.get_coord(event.pos)
                x, y = omok.get_point(coord)
                copy_board = omok.board.copy()
                if copy_board[y][x] != shared.EMPTY:
                    message_box("이미 돌이 놓아진 자리에 놓을 수 없음")
                    continue

                # 금수인지 체크
                node_before = Node(state=board_expand_demand(omok.board),myColor=omok.player_stone,depth=-1)
                from rule import RenjuRule
                rule_tmp = RenjuRule(node_before)
                if rule_tmp.checkForbiddenpoint(y,x,omok.player_stone):
                    message_box("금수 자리입니다")
                    continue

                omok.check_board_and_draw(None,event.pos)
                board = board_expand_demand(omok.board)
                node_tmp = Node(state=board,myColor=omok.player_stone,depth=-1)
                if node_tmp.is_game_over():
                    message_box("플레이어의 승리")
                    game_over = True

        pygame.display.update()
        fps_clock.tick(fps)

class Omok(object):
    def __init__(self, surface,player_stone: int):
        assert player_stone in [shared.BLACK, shared.WHITE]

        self.board = np.zeros((board_size, board_size))
        self.surface = surface
        self.pixel_coords = []
        self.set_coords()
        self.set_image()

        self.turn = black_stone
        self.player_stone = player_stone
        self.draw_board()
        self.coords = []

    def set_image(self):
        black_img = pygame.image.load('gui/image/black.png')
        white_img = pygame.image.load('gui/image/white.png')
        banned_img = pygame.image.load('gui/image/banned.png')
        self.board_img = pygame.image.load('gui/image/board.png')
        self.black_img = pygame.transform.scale(black_img, (grid_size, grid_size))
        self.white_img = pygame.transform.scale(white_img, (grid_size, grid_size))
        self.banned_img = pygame.transform.scale(banned_img, (grid_size, grid_size))

    def is_player_turn(self):
        return self.turn == self.player_stone

    def is_ai_turn(self):
        return not self.is_player_turn()

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

    def convert_yx2coord(self,y,x):
        index = y*15 + x
        return self.pixel_coords[index]

    def check_board_and_draw(self, pos_yx, pos_gui: tuple[int,int]=None):
        if pos_yx is not None:
            y,x = pos_yx
            coord = self.convert_yx2coord(y,x)
            if not coord:
                print("오류 : coord None",file=sys.stderr)
                return False
        else:
            coord = self.get_coord(pos_gui)
            if not coord:
                return False
            x, y = self.get_point(coord)
        if self.board[y][x] != empty:
            return True

        # TODO : 여기에 if문으로 금수 체크

        self.coords.append(coord)
        self.draw_stone(coord, self.turn)
        return True

def board_expand_demand(board: np.ndarray):
    """
    (15,15) -> (15,15,1)
    :param board:
    :return:
    """
    board_new=np.zeros((15,15,1),dtype=np.int32)
    for i in range(len(board_new)):
        for j in range(len(board_new)):
            board_new[i][j][0] = board[i][j]
    return board_new

def start_ai_thread(omok: Omok, valueBool: False):
    global game_over
    from node import Node
    from mcts_module import MCTS
    PLAYER_STONE = omok.player_stone
    AI_STONE = shared.WHITE if PLAYER_STONE == shared.BLACK else shared.BLACK
    tree = MCTS()
    shared.mcts_tree = tree
    board = np.zeros((15, 15, 1), int)
    node = Node(board, shared.BLACK, 0)
    node.print_state()
    depth = 0 if omok.player_stone == shared.WHITE else 1
    while True:
        if not omok.is_ai_turn():
            time.sleep(0.3)
            continue
        node = Node(board_expand_demand(omok.board),AI_STONE,depth)  # 플레이어가 갱신한 노드를 받아오기
        # AI 차례인 경우
        # while True:
        for _ in range(shared.MAX_ROLLOUT):  # mcts 탐색 횟수
            tree.rollout(node, valueBool)  # current board = node
        next_node: Node = tree.move(node)  # board를 선택한 다음 node로 바꿈
        next_node.print_state()
        y,x = next_node.last_yx
        print(f"AI가 선택한 위치 : {y},{x}")
        # node.set_stone(y, x, AI_STONE)
        omok.check_board_and_draw((y,x))
        # omok.draw_stone((x,y),AI_STONE)
        depth+=2
        if next_node.is_game_over():
            message_box("컴퓨터의 승리")
            game_over = True
            return

        # while True:
        #     y, x = map(int, input("사용자 좌표를 y,x순으로 입력하고 스페이스바로 분리 (0부터 14까지)").split())
        #     if y < 0 or y > 14 or x < 0 or x > 14:
        #         print("잘못된 입력 : 0~14사이로 입력하세요")
        #         continue
        #     if next_node.is_stone_exist(y, x):
        #         print("이미 돌이 놔져있는 자리 -> 다시 선택")
        #         continue
        #     break
        # y,x = next_node.last_yx
        # node = Node(next_node.get_state(), PLAYER_STONE, next_node.depth + 1)
        # node.set_stone(y, x, PLAYER_STONE)
        # if node.is_game_over():
        #     print("플레이어가 이겼습니다")
        #     return
        # node.next_color()




def start_game():
    main(player_stone=shared.WHITE)

def message_box(message):
    from tkinter import messagebox
    messagebox.showwarning("경고",message)