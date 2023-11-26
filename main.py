import os
from collections import defaultdict



import numpy as np

import shared
import utils
from mcts_module import MCTS
from gui.main import start_game
from node import Node
from rule import RenjuRule

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# model1 = keras.models.load_model("policy_black.h5")
# model2 = keras.models.load_model("policy_white.h5")





# random하게 다음 node 선택
# cnn에 의해 rollout
# rule에 의해 승리 결정
# backpropagation 이후 reward가 가장 높은 곳으로 move
# 탐색된 node는 children에 포함돼있어야함


MAX_ROLL_OUT = 20
# def game():
#     global MAX_ROLL_OUT
#     PLAYER_STONE = shared.WHITE  # 일단 플레이어는 백만 가정
#     AI_STONE = shared.BLACK
#     tree = MCTS()
#     shared.mcts_tree = tree
#     board = np.zeros((15,15,1), int)
#     node = Node(board,AI_STONE,0) # 흑돌이라고 가정
#     while True:
#         for _ in range(MAX_ROLL_OUT): # mcts 탐색 횟수
#             tree.rollout(node) # current board = node
#         next_node: Node = tree.move(node) # board를 선택한 다음 node로 바꿈
#         next_node.print_state()
#         if next_node.is_game_over():
#             print("콤퓨타가 이겼습니다")
#             return
#         while True:
#             y,x=map(int,input("사용자 좌표를 y,x순으로 입력하고 스페이스바로 분리 (0부터 14까지)").split())
#             if y < 0 or y > 14 or x < 0 or x > 14:
#                 print("잘못된 입력 : 0~14사이로 입력하세요")
#                 continue
#             if next_node.is_stone_exist(y,x):
#                 print("이미 돌이 놔져있는 자리 -> 다시 선택")
#                 continue
#             break
#         node = Node(next_node.get_state(),PLAYER_STONE,next_node.depth+1)
#         node.set_stone(y,x,PLAYER_STONE)
#         if node.is_game_over():
#             print("플레이어가 이겼습니다")
#             return
#         node.next_color()




if __name__ == '__main__':
    # mode=  input("1 : CLI / 2: GUI")
    # mode = mode.strip()
    # if mode == "1":
    #     game()
    # elif mode == "2":
    start_game()
