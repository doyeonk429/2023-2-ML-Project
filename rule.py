
from typing import TYPE_CHECKING

import shared

if TYPE_CHECKING:
    from node import Node


# black_stone = 1
# white_stone = 2
# last_b_stone = 3
# last_a_stont = 4
# tie = 100



class RenjuRule:
    
    # game.py에서 보드 넘겨주기
    def __init__(self, node: 'Node'):
        # TODO : 사용처 제거 및 수정
        self.node = node
        self.board_size = len(self.node.get_state())  # 15 * 15

    # 착수 위치가 오목판 안의 좌표인지 체크
    def isInvalid(self, y,x):
        return (x < 0 or x >= self.board_size or y < 0 or y >= self.board_size)

    # 해당 좌표에 돌이 놓아지는 경우 시뮬레이션
    def setStone(self, y, x, stone, force=True):
        self.node.set_stone(y,x,stone,force)

    # 주변 8방향 리스트
    def getDirection(self, direction):
        list_dx = [-1, 1, -1, 1, 0, 0, 1, -1]
        list_dy = [0, 0, -1, 1, -1, 1, -1, 1]
        return list_dy[direction],list_dx[direction]

    # 주변 돌 개수 세기
    def getCount(self,  y,x, stone, direction):
        y1, x1 = y, x
        cnt = 1
        for i in range(2):
            dy,dx = self.getDirection(direction * 2 + i)
            y, x = y1, x1
            while True:
                y, x = y + dy, x + dx
                if self.isInvalid(y, x) or self.node.get_stone(y,x) != stone:
                    break
                else:
                    cnt += 1
        return cnt
    
    # 오목 완성 -> 승패 결정

    def isGameover(self, y,x):
        """
        안끝났으면 0
        흑이 이기면 1
        백이 이기면 2
        무승부면 0.5
        :param y:
        :param x:
        :return:
        """
        for stone in [shared.BLACK, shared.WHITE]:
            for i in range(4):
                cnt = self.getCount(y,x, stone, i)
                if cnt >= 5:
                    if stone == shared.BLACK:
                        return 1
                    else:
                        return 2
        # 아예 모든 판이 꽉찬 경우
        if self.isFullBoard():
            return 0.5
        return 0

    def isFullBoard(self):
        return self.node.is_full_board()

    # 6목 이상인 경우 체크: 흑돌은 장목 불가룰
    def isSix(self, y,x, stone):
        for i in range(4):
            cnt = self.getCount(y,x, stone, i)
            if cnt > 5:
                return True
        return False

    # 오목인지 체크
    def isFive(self, y,x, stone):
        for i in range(4):
            cnt = self.getCount(y,x, stone, i)
            if cnt == 5:
                return True
        return False

    # 주변 빈자리 체크
    def findEmptypoint(self,y,x, stone, direction):
        # dy, dx = self.get_xy(direction)
        dy, dx = self.getDirection(direction)
        while True:
            y,x =  y + dy,x + dx
            if self.isInvalid(y,x) or self.node.get_stone(y,x) != stone:
                break
        if not self.isInvalid(y,x) and self.node.get_stone(y,x) == shared.EMPTY:
            return y,x # 돌 없는 좌표를 반환
        else:
            return None
        
    # 열린 3 체크
    def checkOpenThree(self, y,x, stone, direction):
        for i in range(2):
            coord = self.findEmptypoint(y,x, stone, direction * 2 + i)
            if coord:
                dy,dx = coord
                self.setStone(dy, dx, stone)
                if 1 == self.checkOpenFour(dy, dx, stone, direction):
                    if not self.checkForbiddenpoint(dy, dx, stone):
                        self.setStone(dy, dx, shared.EMPTY)
                        return True
                self.setStone(dy, dx, shared.EMPTY)
        return False

    # 열린 4 체크
    def checkOpenFour(self, y,x, stone, direction):
        if self.isFive(y,x, stone):
            return False
        cnt = 0
        for i in range(2):
            coord = self.findEmptypoint(y,x, stone, direction * 2 + i)
            if coord:
                if self.isTotalFive(coord[0], coord[1], stone, direction):
                    cnt += 1
        if cnt == 2:
            if 4 == self.getCount(y,x, stone, direction):
                cnt = 1
        else: cnt = 0
        return cnt

    # 4목 체크
    def isFour(self, y,x, stone, direction):
        for i in range(2):
            coord = self.findEmptypoint(y,x, stone, direction * 2 + i)
            if coord:
                if self.isTotalFive(coord[0], coord[1], stone, direction):
                    return True
        return False

    # 한방향 5목 체크
    def isTotalFive(self,  y,x, stone, direction):
        if 5 == self.getCount(y, x,stone, direction):
            return True
        return False

    # 33 패턴 체크
    def checkDoubleThree(self, y,x, stone):
        cnt = 0
        self.setStone(y, x, stone)
        for i in range(4):
            if self.checkOpenThree(y,x, stone, i):
                cnt += 1
        self.setStone(y, x, shared.EMPTY)
        if cnt >= 2:
            # print("33")
            return True
        return False

    # 44 패턴 체크
    def checkDoubleFour(self, y,x, stone):
        cnt = 0
        self.setStone(y, x, stone)
        for i in range(4):
            if self.checkOpenFour(y, x, stone, i) == 2:
                cnt += 2
            elif self.isFour(y, x, stone, i):
                cnt += 1
        self.setStone(y, x, shared.EMPTY)
        if cnt >= 2:
            # print("44")
            return True
        return False

    # 금수 판정
    def checkForbiddenpoint(self, y, x, stone):
        if self.isFive(y, x, stone): return False
        elif self.isSix(y, x, stone):
            # print("6목")
            return True
        elif self.checkDoubleThree(y, x, stone) or self.checkDoubleFour(y, x, stone): return True
        
        return False
    
    
    # 금수 좌표 반환
    # def get_forbidden_points(self, stone):
    #     coords = []
    #     for y in range(len(self.board)):
    #         for x in range(len(self.board[0])):
    #             if self.board[y][x] : continue
    #             if self.checkForbiddenpoint(y, x, stone) : coords.append((y, x))
    #     return [(y,x) for x,y in coords]