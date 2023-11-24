import os
from collections import defaultdict
from collections import namedtuple

import keras
import numpy as np

from rule import RenjuRule

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

model1 = keras.models.load_model("policy_black.h5")
model2 = keras.models.load_model("policy_white.h5")

class Node:
    def __init__(self, state, myColor):
        self.state = state # 흑돌 = 1, 백돌 = 2 : 행렬 인덱스에 저장됨 나머지 0이거나 None일것
        self.myColor = myColor

    def isLeaf(self):
        # 오목 완성 또는 무승부인 상황이면 True, 진행 중이면 False
        rule = RenjuRule(self.state, 15*15)
        x, y = self.state.cnn_predict_pos()
        over1 = rule.isGameover(x,y,1)
        over2 = rule.isGameover(x,y,2)
        if over1 or over2:
            return True
        return False

    def getReward(self):
        if self.myColor == 1:
            if self.state.count(1) > self.state.count(2): # 흑돌오목
                return 1
            elif self.state.count(1) > self.state.count(1): # 백돌 오목 및 장목
                return 0


    def getChildren(self):
        # 금수 제외 가능한 모든 다음 노드 찾기 # 가능한 children node들의 집합 set() 반환
        childrenSet = set()
        if self.myColor == 1:
            if self.state[0] != 1 and self.state[0] != 2 :
                childNode = self.state
                childNode[i] = 1
                childrenSet.add(childNode)
            return childrenSet      # 금수 제외 안했음
        else:
            for i in self.state:
                for j in self.state:
                    if self.state[i] != 1 and self.state[i] != 2:
                        childNode = self.state
                        childNode[i] = 2
                        childrenSet.add(childNode)
            return childrenSet

    def cnn_predict(self, turn):
        # 현재 상태에서 cnn predict
        if turn:
            y_predict = model2.predict(self.state)
            index = np.argmax(y_predict)
            y = index / 15
            x = index % 15

            self.state[y][x] = 2
        else:
            y_predict = model1.predict(self.state)
            index = np.argmax(y_predict)
            y = index / 15
            x = index % 15

            self.state[y][x] = 1

        return self.state

    def cnn_predict_pos(self):
        y_predict = model2.predict(self.state)
        index = np.argmax(y_predict)
        y = index / 15
        x = index % 15

        return x, y

    def __hash__(self):
        return hash(self.state)

# random하게 다음 node 선택
# cnn에 의해 rollout
# rule에 의해 승리 결정
# backpropagation 이후 reward가 가장 높은 곳으로 move
# 탐색된 node는 children에 포함돼있어야함

class MCTS:
    def __init__(self):
        self.Q = defaultdict(int)         # 각 노드의 총 reward
        self.N = defaultdict(int)         # 각 노드의 총 방문횟수
        self.children = {}  # 각 노드의 children

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

        return max(self.children[node], key=score)

    def rollout(self, node):
        # 결과 도출 및 backpropagation 실행까지.
        path = self.select(node)            # root부터 탐색할 node까지의 path
        leaf = path[-1]                     # leaf node 할당
        self.expand(leaf)                   # leaf에서 확장 시도 leaf는 key가 되고 children이 생김(탐색증거)
        reward = self.simulate(leaf)        # leaf에서 simulate 진행
        self.backpropagate(reward, path)    # 승률 역전파

    def select(self, node):
        # 탐색되지 않은 노드 선택
        path = []
        while True:
            path.append(node)
            if node not in self.children or not self.children[node]: # key도 value도 아닌 node이면
                return path
            unexplored = self.children[node] - self.children.keys() # children인 node set - 탐색한 node set

            # unexplored node가 존재한다면 먼저 탐색
            if unexplored:
                nextLeaf = unexplored.pop()
                path.append(nextLeaf)
                return path

            # 모든 노드가 확장되고 탐색됨 -> uct를 통해 재탐색
            node = self.uct(node)

    def expand(self, node):
        # 확장된 적 없으면 확장 (children dict의 key가 아니므로)
        if node not in self.children:
            self.children[node] = node.getChildren()

    def simulate(self, node):
        # cnn 반복하여 reward 반환
        # 흑과 백 cnn 각각 실행반복하여 terminal 도달 후 reward 반환
        opponent_win = True # 홀수번째 simulate에서 게임종료 -> 상대방 승
        over = False

        while True:
            rule = RenjuRule(node, 15*15)
            if over:
                reward = node.getReward()
                if opponent_win:
                    return 1 - reward
                else:
                    return reward

            node = node.cnn_predict(opponent_win)
            x, y = node.cnn_predict_pos()
            if opponent_win:
                over = rule.isGameover(x,y,2)
            else:
                over = rule.isGameover(x,y,1)

            opponent_win = not opponent_win  # 짝수번째에서 게임종료이면 나의 승


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


def game():
    tree = MCTS()
    list1 = []

    board = namedtuple('board', 'index')
    board = board(index=(0,) * 225)
    node = Node(board,1) # 흑돌이라고 가정
    while True:
        for _ in range(100): # mcts 탐색 횟수
            tree.rollout(node) # current board = node
        board = tree.move(node) # board를 선택한 다음 node로 바꿈
        print(node)

game()


