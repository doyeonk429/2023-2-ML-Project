from typing import Tuple

from numpy import ndarray


import numpy as np

import shared
import utils
from rule import RenjuRule


class Node:
    def __init__(self, state: np.ndarray, myColor: int, depth: int):
        self._state: np.ndarray = state.copy() # 흑돌 = 1, 백돌 = 2 : 행렬 인덱스에 저장됨 나머지 0이거나 None일것
        assert self._state.shape[2] == 1, f"점검 필요 : {self._state.shape}"
        self.myColor = myColor
        self.depth = depth
        self.last_yx = None

    def get_board_size(self) -> tuple[int, ...]:
        return self._state.shape

    def get_state(self) -> np.ndarray:
        return self._state

    def isLeaf(self):
        # 오목 완성 또는 무승부인 상황이면 True, 진행 중이면 False
        rule = RenjuRule(self)
        y, x, action_probs = self.cnn_predict() # TODO : 오류날수도
        over1 = rule.isGameover(y,x,shared.BLACK)
        over2 = rule.isGameover(y,x,shared.WHITE)
        if over1 or over2:
            return True
        return False

    # 23.11.25 수정
    def getReward(self):
        black_cnt = self.get_stone_count(shared.BLACK)
        white_cnt = self.get_stone_count(shared.WHITE)
        if black_cnt == white_cnt:
            return 0.5
        if self.myColor == shared.BLACK:
            if black_cnt > white_cnt:
                return 1
            else:
                return 0
        else:
            if black_cnt > white_cnt:
                return 0
            else:
                return 1
        # if self.myColor == 1:
        #     if self.get_stone_count(shared.BLACK) > self.get_stone_count(shared.WHITE): # 흑돌오목
        #         return 1
        #     else:
        #         if self.get_stone_count(shared.WHITE) > self.get_stone_count(shared.BLACK): # 백돌 오목 및 장목
        #             return 0
        #         else:
        #             return


    def get_stone_count(self, stone: int):
        assert stone in [shared.BLACK, shared.WHITE]
        return sum(1 for num in list(self._state.flat) if num == stone)

    def __eq__(self, other):
        return np.array_equal(self._state,other.get_state())

    def __hash__(self):
        return hash(self._state)

    def get_stone(self, y, x):
        assert len(self._state[y][x]) == 1
        return self._state[y][x][0]

    def set_stone(self,y,x,color,force=False):
        # print("set_stone : ",y,x,color)
        if not force and self._state[y][x][0] != shared.EMPTY:
            raise Exception("이미 돌이 놓여있는 곳 -> 디버그 필요")
        self._state[y][x][0] = color
        if not force:
            self.last_yx = (y,x)




    def getChildren(self):
        # 금수 제외 가능한 모든 다음 노드 찾기 # 가능한 children node들의 집합 set() 반환
        childrenSet = set()
        cur_depth = self.depth
        for i in range(len(self._state)):
            for j in range(len(self._state)):
                # TODO : 0,0에서 바로 끝나네
                if self.get_stone(i,j) != shared.BLACK and self.get_stone(i,j) != shared.WHITE:
                    childNode: Node = Node(self._state,self.myColor,cur_depth+1)
                    childNode.set_stone(i,j,self.myColor)
                    childrenSet.add(childNode)
                return childrenSet  # 금수 제외 안했음
        # if self.myColor == BLACK:
        #     for i in range(len(self.state)):
        #         for j in range(len(self.state)):
        #             if self.state[i][j] != BLACK and self.state[i][j] != WHITE :
        #                 childNode: Node = Node(self.state)
        #                 childNode.state[i][j] = self.myColor
        #                 childrenSet.add(childNode)
        #             return childrenSet      # 금수 제외 안했음
        # else:
        #     for i in range(len(self.state)):
        #         for j in range(len(self.state)):
        #             if self.state[i][j] != BLACK and self.state[i][j] != WHITE:
        #                 childNode: Node = Node(self.state)
        #                 childNode.state[i][j] = self.myColor
        #                 childrenSet.add(childNode)
        #     return childrenSet

    def is_game_over(self):
        """
        0이면 아직 안끝나고
        0.5면 무승부
        1이면 흑이 이기고
        2면 백이 이김
        :param board:
        :return:
        """
        if self.is_full_board():
            return 0.5

        board = self.get_state()

        def check_win(player):
            dydx=[(0, 1), (1, 0), (0, -1), (-1, 0), (1, -1), (-1, 1), (1, 1), (-1, -1)]
            board_len = self.get_board_size()[0]
            for i in range(board_len):
                for j in range(board_len):
                    if board[i][j] == player:
                        for dy, dx in dydx:
                            cnt = 1
                            nx, ny = j + dx, i + dy
                            while 0 <= nx < board_len and 0 <= ny < board_len and board[ny][nx] == player:
                                cnt += 1
                                nx += dx
                                ny += dy
                                if cnt >= 5:
                                    return True
        is_black_win = check_win(shared.BLACK)
        is_white_win = check_win(shared.WHITE)
        assert not (is_black_win and is_white_win), "둘다 이길 수 없음 -> 점검하기"
        if is_black_win:
            return shared.BLACK
        elif is_white_win:
            return shared.WHITE
        else:
            return 0

    def predict_value_net(self):
        turn = self.myColor
        assert type(turn) == int and turn in [shared.BLACK, shared.WHITE]
        # 현재 상태에서 cnn predict

        inputs = utils.reshape_to_15_15_1(self._state)
        value = shared.value_model.predict(inputs)

        # 흑을 기준으로 가치망 학습 -> 백은 음수로 변경
        if turn == shared.WHITE:
            value = -value

        return value


    def cnn_predict(self) -> tuple[int,int,ndarray]:
        turn = self.myColor
        assert type(turn) == int and turn in [shared.BLACK, shared.WHITE]
        # 현재 상태에서 cnn predict

        inputs = utils.reshape_to_15_15_1(self._state)
        rule = RenjuRule(self)

        # print("예측을 위해 사용한 돌 : ",turn)
        use_model = shared.model1 if turn == shared.BLACK else shared.model2
        # 23.11.25 수정 -> int
        y_predict = use_model.predict(inputs)

        # 이미 돌이 놔져 있는 곳은 또 놓을 수 없으니 확률 값을 아예 0으로 바꿔서 argmax에서 고를 일이 없도록 설정
        board_len = self.get_board_size()[0]
        for i in range(board_len):
            for j in range(board_len):
                stone_state =self.get_stone(i,j)
                # 빈자리이거나 금수 자리일 경우 확률 0으로
                if stone_state != shared.EMPTY or (stone_state == shared.EMPTY and rule.checkForbiddenpoint(i,j,turn)):
                    y_predict[0][i * board_len + j] = 0

        # 금수 자리도 0으로


        index = np.argmax(y_predict)
        y = index // 15  # 23.11.25 수정 -> int
        x = index % 15

        if y_predict[0][index] == 0:
            raise Exception("최댓값으로 고른 자리의 확률이 0")


        # if turn:
        #     y_predict = shared.model2.predict(inputs)
        #     index = np.argmax(y_predict)
        #     y = index // 15 # 23.11.25 수정 -> int
        #     x = index % 15
        # else:
        #     y_predict = shared.model1.predict(inputs)
        #     index = np.argmax(y_predict)
        #     y = index // 15
        #     x = index % 15

        return y,x,y_predict[0]

    def __str__(self):
        return f"깊이 : {self.depth}"

    # def cnn_predict_pos(self):
    #     inputs = utils.reshape_to_15_15_1(self.state)
    #     y_predict = model2.predict(inputs)
    #     index = np.argmax(y_predict)
    #     y = index // 15  # 나누기 수정
    #     x = index % 15
    #     return x, y

    def print_state(self):
        state = self.get_state()
        emoji = ["⬜","⚫", "🔘"] # 후보 : 🔘 🔵 🟠 🟣 ⚪ 🟡 🟤 ⚫ ㊙️ ㊗️
        for i in range(len(state)):
            for j in range(len(state)):
                print(emoji[state[i][j][0]], end=" ")
            print()

    def is_stone_exist(self,y,x):
        return self.get_stone(y,x) != shared.EMPTY

    def __hash__(self):
        # return hash(tuple(self.state))
        return hash("".join(map(str, list(self.get_state().flat))))
        # return hash(tuple(map(tuple, self.state)))

    def is_full_board(self):
        empty = shared.EMPTY
        board_len = self.get_board_size()[0]
        for y in range(board_len):
            for x in range(board_len):
                if self.get_stone(y, x) == empty:
                    return False
        return True

    def next_color(self):
        self.myColor = utils.change_color(self.myColor)
