empty = 0
# black_stone = 1
# white_stone = 2
# last_b_stone = 3
# last_a_stont = 4
# tie = 100

class RenjuRule(object):
    
    # game.py에서 보드 넘겨주기
    def __init__(self, board, board_size):
        self.board = board
        self.board_size = board_size # 15 * 15

    # 착수 위치가 오목판 안의 좌표인지 체크
    def isInvalid(self, x, y): 
        return (x < 0 or x >= self.board_size or y < 0 or y >= self.board_size)

    # 해당 좌표에 돌이 놓아지는 경우 시뮬레이션
    def setStone(self, x, y, stone): 
        self.board[y][x] = stone

    # 주변 8방향 리스트
    def getDirection(self, direction): 
        list_dx = [-1, 1, -1, 1, 0, 0, 1, -1]
        list_dy = [0, 0, -1, 1, -1, 1, -1, 1]
        return list_dx[direction], list_dy[direction]

    # 주변 돌 개수 세기
    def getCount(self, x, y, stone, direction): 
        x1, y1 = x, y
        cnt = 1
        for i in range(2):
            dx, dy = self.getDirection(direction * 2 + i)
            x, y = x1, y1
            while True:
                x, y = x + dx, y + dy
                if self.isInvalid(x, y) or self.board[y][x] != stone:
                    break
                else:
                    cnt += 1
        return cnt
    
    # 오목 완성 -> 승패 결정
    def isGameover(self, x, y, stone):
        for i in range(4):
            cnt = self.getCount(x, y, stone, i)
            if cnt >= 5:
                return True
        return False

    # 6목 이상인 경우 체크: 흑돌은 장목 불가룰
    def isSix(self, x, y, stone): 
        for i in range(4):
            cnt = self.getCount(x, y, stone, i)
            if cnt > 5:
                return True
        return False

    # 오목인지 체크
    def isFive(self, x, y, stone): 
        for i in range(4):
            cnt = self.getCount(x, y, stone, i)
            if cnt == 5:
                return True
        return False

    # 주변 빈자리 체크
    def findEmptypoint(self, x, y, stone, direction): 
        dx, dy = self.get_xy(direction)
        while True:
            x, y = x + dx, y + dy
            if self.isInvalid(x, y) or self.board[y][x] != stone:
                break
        if not self.isInvalid(x, y) and self.board[y][x] == empty:
            return x, y # 돌 없는 좌표를 반환
        else:
            return None
        
    # 열린 3 체크
    def checkOpenThree(self, x, y, stone, direction):
        for i in range(2):
            coord = self.findEmptypoint(x, y, stone, direction * 2 + i)
            if coord:
                dx, dy = coord
                self.setStone(dx, dy, stone)
                if 1 == self.checkOpenFour(dx, dy, stone, direction):
                    if not self.checkForbiddenpoint(dx, dy, stone):
                        self.setStone(dx, dy, empty)
                        return True
                self.setStone(dx, dy, empty)
        return False

    # 열린 4 체크
    def checkOpenFour(self, x, y, stone, direction):
        if self.isFive(x, y, stone):
            return False
        cnt = 0
        for i in range(2):
            coord = self.findEmptypoint(x, y, stone, direction * 2 + i)
            if coord:
                if self.isTotalFive(coord[0], coord[1], stone, direction):
                    cnt += 1
        if cnt == 2:
            if 4 == self.getCount(x, y, stone, direction):
                cnt = 1
        else: cnt = 0
        return cnt

    # 4목 체크
    def isFour(self, x, y, stone, direction):
        for i in range(2):
            coord = self.findEmptypoint(x, y, stone, direction * 2 + i)
            if coord:
                if self.isTotalFive(coord[0], coord[1], stone, direction):
                    return True
        return False

    # 한방향 5목 체크
    def isTotalFive(self, x, y, stone, direction):
        if 5 == self.getCount(x, y, stone, direction):
            return True
        return False

    # 33 패턴 체크
    def checkDoubleThree(self, x, y, stone):
        cnt = 0
        self.setStone(x, y, stone)
        for i in range(4):
            if self.checkOpenThree(x, y, stone, i):
                cnt += 1
        self.setStone(x, y, empty)
        if cnt >= 2:
            # print("33")
            return True
        return False

    # 44 패턴 체크
    def checkDoubleFour(self, x, y, stone):
        cnt = 0
        self.setStone(x, y, stone)
        for i in range(4):
            if self.checkOpenFour(x, y, stone, i) == 2:
                cnt += 2
            elif self.isFour(x, y, stone, i):
                cnt += 1
        self.setStone(x, y, empty)
        if cnt >= 2:
            # print("44")
            return True
        return False

    # 금수 판정
    def checkForbiddenpoint(self, x, y, stone):
        if self.isFive(x, y, stone): return False
        elif self.isSix(x, y, stone):
            # print("6목")
            return True
        elif self.checkDoubleThree(x, y, stone) or self.checkDoubleFour(x, y, stone): return True
        
        return False
    
    
    # 금수 좌표 반환
    # def get_forbidden_points(self, stone):
    #     coords = []
    #     for y in range(len(self.board)):
    #         for x in range(len(self.board[0])):
    #             if self.board[y][x] : continue
    #             if self.checkForbiddenpoint(x, y, stone) : coords.append((x, y))
    #     return [(y,x) for x,y in coords]