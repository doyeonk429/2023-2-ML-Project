import os
from collections import defaultdict



import numpy as np

import shared
import utils
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

class MCTS:
    def __init__(self):
        self.Q = defaultdict(int)         # 각 노드의 총 reward
        self.N = defaultdict(int)         # 각 노드의 총 방문횟수
        self.children: dict[str,set] = {}  # 각 노드의 children


    def is_leaf_node(self, node: Node):
        # 오목 완성 또는 무승부인 상황이면 True, 진행 중이면 False
        if node not in self.children or len(self.children[node])==0:
            return True
        return False

    def move(self, node):
        # 승률 가장 높은 노드 선택하여 착수
        # over1, over2 = False, False
        # rule = RenjuRule(node, 15*15)
        # over1 = rule.isGameover(x, y, 1)
        # over2 = rule.isGameover(x, y, 2)
        # if over1 or over2:
        #     return # game is already over

        # 승률 가장 높은 child node 선택
        def score(i):
            if self.N[i] == 0:
                return float("-inf")
            return self.Q[i] / self.N[i]

        assert node in self.children, f"node is not in children : hash {node.__hash__()}"
        return max(self.children[node], key=score)

    def rollout(self, node):
        assert type(node) == Node
        # 결과 도출 및 backpropagation 실행까지.
        path_nodes = None
        while True:
            if self.is_leaf_node(node):
                break
            path_nodes = self.select(node) # TODO : action도 받아야함?
            node = path_nodes[-1]
            # TODO : 여기서 move?
        # path = self.select(node)         # root부터 탐색할 node까지의 path
        # leaf = path[-1]
        _,_,actions_probs = node.cnn_predict()
        # leaf_value = self.value_net.predict(inputs,verbose=0,steps=1)[0][0]
        # if black_white_ai == 'white': # 가치망은 흑을 기준으로 나와 있으므로 뒤집어야함
        #     leaf_value = -leaf_value

        winner_stone = node.is_game_over() # TODO : make
        reward = 0.5 # TODO : 여기서 0.5 대신에 가치망으로 예측한 승률 값이 들어가면 됨

        end = True if winner_stone else False
        if not end:# leaf node 할당
            self.expand(node,actions_probs,node.myColor)                   # leaf에서 확장 시도 leaf는 key가 되고 children이 생김(탐색증거)
        else:
            if winner_stone == node.myColor:
                reward = 1
            elif winner_stone == 0.5:
                reward = 0  # 무승부는 reward 0
            else:
                reward = -1
            # reward = node.getReward()
        # update_recursive_backpropagate();
        # reward = self.simulate(leaf)        # leaf에서 simulate 진행
        if not path_nodes:
            path_nodes = [node]
        self.backpropagate(reward, path_nodes)    # 승률 역전파

    def select(self, node: Node):
        # 탐색되지 않은 노드 선택
        path: list[Node] = []
        while True:
            print("while돌고 있냐")
            path.append(node)
            if node not in self.children or not self.children[node]: # key도 value도 아닌 node이면
                return path
            unexplored = self.children[node] - self.children.keys() # children인 node set - 탐색한 node set

            print(f"unexplored : {unexplored}")
            # unexplored node가 존재한다면 먼저 탐색
            if unexplored:
                nextLeaf = unexplored.pop()
                path.append(nextLeaf)
                return path

            # 모든 노드가 확장되고 탐색됨 -> uct를 통해 재탐색
            node = self.uct(node)


    def expand(self, node: Node, actions_probs, node_color: int):
        is_black = True if node_color == shared.BLACK else False
        all_childs = set()
        if node in self.children:
            all_childs = self.children[node]
        else:
            self.children[node] = all_childs
        for idx, prob in enumerate(actions_probs):
            # if 흑이면서 금수 자리일 때:
            #     continue
            if prob < 0.1:
                continue
            node_next = Node(node.get_state(), utils.change_color(node_color), node.depth + 1)
            node_next.set_stone(idx // 15, idx % 15, node_color)
            if node_next not in all_childs:
                self.children[node].add(node_next)
                # self._children[action] = TreeNode(self, prob,self.depth+1)

    # def expand(self, node):
    #     확장된 적 없으면 확장 (children dict의 key가 아니므로)
        # print(f"expand : {node.depth}")
        # if node not in self.children:
        #     self.children[node] = node.getChildren()


    # def simulate(self, node: Node):
    #     print("simulate 함수 호출")
    #     # cnn 반복하여 reward 반환
    #     # 흑과 백 cnn 각각 실행반복하여 terminal 도달 후 reward 반환
    #     over = False
    #
    #     if node.is_full_board():
    #         return 0.5
    #
    #     # 23.11.25 -> 무한 루프 오류 있음
    #     while True:
    #         rule = RenjuRule(node)
    #         y,x = node.cnn_predict()
    #         print(f"예측한 위치 : {y},{x}, 깊이 : {node.depth}")
    #         over = rule.isGameover(y,x)
    #         # if opponent_win:
    #         #     over = rule.isGameover(y,x)
    #         # else:
    #         #     over = rule.isGameover(y,x,1)
    #         if over:
    #             opponent_win = False if node.myColor == over else True
    #             reward = node.getReward()
    #             if opponent_win:
    #                 return 1 - reward
    #             else:
    #                 return reward
    #
    #         next_color = utils.change_color(node.myColor)
    #         node = Node(node.get_state(), next_color, node.depth + 1)
    #         node.set_stone(y,x, next_color)
    #         print("node 깊이 : ",node.depth)



    def backpropagate(self, reward, path):
        # 부모 노드에 reward 전달
        for node in path[::-1]:
            self.Q[node] += reward
            self.N[node] += 1
            reward = 1 - reward # 상대에겐 reward 주면 안됨

    def uct(self, node):
        ln_n = np.log(self.N[node])

        def uct_formula(n):
            return (self.Q[n] / self.N[n]) * np.sqrt(2 * ln_n / self.N[n])

        return max(self.children[node], key=uct_formula)


MAX_ROLL_OUT = 20
def game():
    global MAX_ROLL_OUT
    PLAYER_STONE = shared.WHITE  # 일단 플레이어는 백만 가정
    AI_STONE = shared.BLACK
    tree = MCTS()
    board = np.zeros((15,15,1), int)
    node = Node(board,AI_STONE,0) # 흑돌이라고 가정
    while True:
        for _ in range(MAX_ROLL_OUT): # mcts 탐색 횟수
            tree.rollout(node) # current board = node
        next_node: Node = tree.move(node) # board를 선택한 다음 node로 바꿈
        next_node.print_state()
        if next_node.is_game_over():
            print("콤퓨타가 이겼습니다")
            return
        while True:
            y,x=map(int,input("사용자 좌표를 y,x순으로 입력하고 스페이스바로 분리 (0부터 14까지)").split())
            if y < 0 or y > 14 or x < 0 or x > 14:
                print("잘못된 입력 : 0~14사이로 입력하세요")
                continue
            break
        node = Node(next_node.get_state(),PLAYER_STONE,next_node.depth+1)
        node.set_stone(y,x,PLAYER_STONE)
        if node.is_game_over():
            print("플레이어가 이겼습니다")
            return
        node.next_color()




game()
