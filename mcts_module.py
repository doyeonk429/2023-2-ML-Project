import numpy as np
from collections import defaultdict

import shared
import utils
from node import Node
from rule import RenjuRule

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

    def rollout(self, node, use_value_net: bool = True):
        assert type(node) == Node
        # 결과 도출 및 backpropagation 실행까지.
        path_nodes = None
        while True:
            if self.is_leaf_node(node):
                break
            path_nodes = self.select(node) # TODO : action도 받아야함?
            node = path_nodes[-1]
        # path = self.select(node)         # root부터 탐색할 node까지의 path
        # leaf = path[-1]
        _,_,actions_probs = node.cnn_predict()
        # leaf_value = self.value_net.predict(inputs,verbose=0,steps=1)[0][0]
        # if black_white_ai == 'white': # 가치망은 흑을 기준으로 나와 있으므로 뒤집어야함
        #     leaf_value = -leaf_value

        winner_stone = node.is_game_over() # TODO : make
        if use_value_net:
            reward = node.predict_value_net()
        else:
            reward = 0.5  # 가치망을 사용하지 않으면 reward는 임시로 0.5

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
            path.append(node)
            if node not in self.children or not self.children[node]: # key도 value도 아닌 node이면
                return path
            unexplored = self.children[node] - self.children.keys() # children인 node set - 탐색한 node set

            # print(f"unexplored : {unexplored}")
            # unexplored node가 존재한다면 먼저 탐색
            if unexplored:
                nextLeaf = unexplored.pop()
                path.append(nextLeaf)
                return path

            # 모든 노드가 확장되고 탐색됨 -> uct를 통해 재탐색
            node = self.uct(node)


    def expand(self, node: Node, actions_probs, node_color: int):
        is_black = True if node_color == shared.BLACK else False
        bound = 0.1
        all_childs = set()
        if node in self.children:
            all_childs = self.children[node]
        else:
            self.children[node] = all_childs

        probs_with_index = list(sorted(list(zip(range(0,225),actions_probs)), key=lambda k: -k[1]))
        probs_upper_bound = list(filter(lambda k: k[1] > bound, probs_with_index))
        # 0.1 확률이 넘는게 없는 경우
        if not probs_upper_bound:
            probs_upper_bound.append(probs_with_index[0])

        for idx,prob in probs_upper_bound:
            node_next = Node(node.get_state(), utils.change_color(node_color), node.depth + 1)
            y,x = idx // 15, idx % 15
            node_next.set_stone(y,x,node_color)
            print("depth :",node.depth)
            if node_next not in all_childs:
                self.children[node].add(node_next)



        #
        # for idx, prob in enumerate(actions_probs):
        #     if prob<bound:
        #         continue
        #     node_next = Node(node.get_state(), utils.change_color(node_color), node.depth + 1)
        #     y,x = idx // 15, idx % 15
        #     node_next.set_stone(y,x,node_color)
        #     if node_next.is_stone_exist(y,x):
        #         continue
        #     print("depth :",node.depth)
        #     if node_next not in all_childs:
        #         self.children[node].add(node_next)
        #         # self._children[action] = TreeNode(self, prob,self.depth+1)



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
