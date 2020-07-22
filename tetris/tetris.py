import sys
import pygame
from pygame.locals import *
import random

class Tetris:
    def __init__(self):
        self.minos = [
            [1, [0, 0], [0, 0], [0, 0]],
            [2, [0, -1], [0, 1], [0, 2]],
            [4, [0, -1], [0, 1], [1, 1]],
            [4, [0, -1], [0, 1], [-1, 1]],
            [2, [0, -1], [1, 0], [1, 1]],
            [2, [0, -1], [-1, 0], [-1, 1]],
            [1, [0, 1], [1, 0], [1, 1]],
            [4, [0, -1], [1, 0], [-1, 0]],
            [2, [0, -1], [0, 1], [0, 2]],
            [4, [0, -1], [0, 1], [1, 1]],
            [4, [0, -1], [0, 1], [-1, 1]],
            [2, [0, -1], [1, 0], [1, 1]],
            [2, [0, -1], [-1, 0], [-1, 1]],
            [1, [0, 1], [1, 0], [1, 1]],
            [4, [0, -1], [1, 0], [-1, 0]]
            ]
        self.board = [[1 for _ in range(45)] if x == 0 or x == 11 else [1 if y == 0 else 0 for y in range(45)] for x in range(12)]
        self.board_hold = [[15 for _ in range(5)] for _ in range(5)]
        self.nexts = [[[15 for _ in range(5)] for _ in range(5)] for _ in range(5)]
        self.attack = []
        self.minoList = [[i for i in range(1,8)] for _ in range(2)]
        random.shuffle(self.minoList[0])
        random.shuffle(self.minoList[1])
        self.cnt = 0
        self.pawer = 0
        self.wall = 0
        self.time = 0
        self.chain = 0
        self.canHold = True
        self.btb = False
        self.mino = [5, 21, 0, 0]
        self.mino[2] = self.selectMino()
        self.block = [i for i in self.mino]
        self.hold = None
        self.fin = False
        self.con = True
        self.se = True
        pygame.init()
        pygame.display.set_caption("Tetris")
        pygame.mixer.music.load("sound_effect/BGM.wav")
        pygame.mixer.music.play(-1)
        self.size1 = 24
        self.size2 = 15
        self.size3 = 20
        self.img1 = pygame.image.load("img.png")
        self.img2 = pygame.transform.scale(self.img1, (self.size2 * 2, self.size2 * 8))
        self.img3 = pygame.transform.scale(self.img1, (self.size3 * 2, self.size3 * 8))
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.size1 * 20 + 20, self.size1 * 20 + 50))
        self.clear = pygame.mixer.Sound("sound_effect/clear.wav")
        self.line = pygame.mixer.Sound("sound_effect/line.wav")
        self.damage = pygame.mixer.Sound("sound_effect/damage.wav")
        self.allClear = pygame.mixer.Sound("sound_effect/allClear.wav")
        self.fall = pygame.mixer.Sound("sound_effect/fall.wav")
        
    def reset(self):
        self.board = [[1 for _ in range(45)] if x == 0 or x == 11 else [1 if y == 0 else 0 for y in range(45)] for x in range(12)]
        self.board_hold = [[15 for _ in range(5)] for _ in range(5)]
        self.nexts = [[[15 for _ in range(5)] for _ in range(5)] for _ in range(5)]
        self.attack = []
        self.minoList = [[i for i in range(1,8)] for _ in range(2)]
        random.shuffle(self.minoList[0])
        random.shuffle(self.minoList[1])
        self.cnt = 0
        self.pawer = 0
        self.wall = 0
        self.time = 0
        self.chain = 0
        self.canHold = True
        self.btb = False
        self.mino = [5, 21, 0, 0]
        self.mino[2] = self.selectMino()
        self.block = [i for i in self.mino]
        self.hold = None
        self.fin = False
        self.con = True
        self.se = True
        pygame.mixer.music.play(-1)
        self.main()
    
    def selectMino(self):
        if self.cnt > 6: self.cnt -= 7
        if self.cnt == 0:
            self.minoList[0] = [i for i in self.minoList[1]]
            random.shuffle(self.minoList[1])
        for n in range(5):
            for x in range(5):
                for y in range(5): self.nexts[n][x][y] = 15
            nxt = self.cnt + n + 1
            list_n = 0
            if nxt > 6:
                nxt -= 7
                list_n = 1
            self.nexts[n][2][2] = self.minoList[list_n][nxt]
            for i in range(3):
                dx = self.minos[self.minoList[list_n][nxt]][i + 1][0]
                dy = self.minos[self.minoList[list_n][nxt]][i + 1][1]
                self.nexts[n][2 + dx][2 + dy] = self.minoList[list_n][nxt]
        for j in range(5):
            for k in range(5): self.nexts[j][k].reverse()
        mino_choice = self.minoList[0][self.cnt]
        self.cnt += 1
        return mino_choice

    def loadBoard(self):
        for x in range(1, 11):
            for y in range(1, 21):
                for i in range(16):
                    img_y = i
                    img_x = 0
                    if i == 15:
                        img_y = 0
                        img_x = self.size1
                    elif i > 7:
                        img_y -= 7
                        img_x = self.size1
                    if self.board[x][y] == i: self.screen.blit(self.img1, ((x + 4) * self.size1 + 10, (20 - y) * self.size1 + 10),
                                                     (img_x, img_y * self.size1, self.size1, self.size1))

        for x in range(5):
            for y in range(5):
                for i in range(16):
                    img_y = i
                    img_x = 0
                    if i == 15:
                        img_y = 0
                        img_x = self.size2
                    elif i > 7:
                        img_y -= 7
                        img_x = self.size2
                    if self.board_hold[x][y] == i: self.screen.blit(self.img2, (x * self.size2 + 45, y * self.size2 + 10),
                                                          (img_x, img_y * self.size2, self.size2, self.size2))

        for n in range(5):
            for x in range(5):
                for y in range(5):
                    for i in range(16):
                        img_y = i
                        img_x = 0
                        if i == 15:
                            img_y = 0
                            img_x = self.size2
                        elif i > 7:
                            img_y -= 7
                            img_x = self.size2
                        if self.nexts[n][x][y] == i: self.screen.blit(self.img2, (15 * self.size1 + x * self.size2 + 15, (n * 5 + y) * self.size2 + 12),
                                                            (img_x, img_y * self.size2, self.size2, self.size2))

        self.attack.reverse()
        for i in range(20):
            if len(self.attack) > i:
                if self.attack[i] > 5: self.screen.blit(self.img3, (100, (19 - i) * self.size3 + 90),
                                              (0, 6 * self.size3, self.size3, self.size3))
                else: self.screen.blit(self.img3, (100, (19 - i) * self.size3 + 90),
                                  (0, 4 * self.size3, self.size3, self.size3))
            else: self.screen.blit(self.img3, (100, (19 - i) * self.size3 + 90),
                              (self.size3, 0 * self.size3, self.size3, self.size3))
        self.attack.reverse()

    def putMino(self, mino, action = False):
        if self.board[mino[0]][mino[1]] != 0 and self.board[mino[0]][mino[1]] < 8\
           or self.board[mino[0]][mino[1]] == 15: return False
        if action: self.board[mino[0]][mino[1]] = mino[2]
        for i in range(3):
            dx = self.minos[mino[2]][i + 1][0]
            dy = self.minos[mino[2]][i + 1][1]
            r = mino[3] % self.minos[mino[2]][0]
            for j in range(r):
                dx, dy = dy, -dx
            if self.board[mino[0] + dx][mino[1] + dy] != 0 and self.board[mino[0] + dx][mino[1] + dy] < 8\
               or self.board[mino[0] + dx][mino[1] + dy] == 15:return False
            if action: self.board[mino[0] + dx][mino[1] + dy] = mino[2]
        if not action: self.putMino(mino, True)
        return True

    def deleteMino(self, mino):
        self.board[mino[0]][mino[1]] = 0
        for i in range(3):
            dx = self.minos[mino[2]][i + 1][0]
            dy = self.minos[mino[2]][i + 1][1]
            r = mino[3] % self.minos[mino[2]][0]
            for j in range(r): dx, dy = dy, -dx
            self.board[mino[0] + dx][mino[1] + dy] = 0

    def hardDrop(self):
        for y in range(20, 0, -1):
            for x in range(1, 11):
                if self.board[x][y] > 7 and self.board[x][y] != 15: self.board[x][y] = 0
        temp = [[] for i in range(4)]
        for i in range(3):
            dx = self.minos[self.mino[2]][i + 1][0]
            dy = self.minos[self.mino[2]][i + 1][1]
            r = self.mino[3] % self.minos[self.mino[2]][0]
            for j in range(r): dx, dy = dy, -dx
            temp[i] = [self.mino[0] + dx, self.mino[1] + dy]
        temp[3] = [self.mino[0], self.mino[1]]
        self.block = [i for i in self.mino]
        self.block[2] += 7
        overlap = 4
        while overlap != 0:
            overlap = 0
            self.block[1] -= 1
            if [self.block[0], self.block[1]] in temp: overlap += 1
            for i in range(3):
                dx = self.minos[self.block[2]][i + 1][0]
                dy = self.minos[self.block[2]][i + 1][1]
                r = self.block[3] % self.minos[self.block[2]][0]
                for j in range(r): dx, dy = dy, -dx
                if [self.block[0] + dx, self.block[1] + dy] in temp: overlap += 1
        if self.putMino(self.block):
            while self.putMino(self.block):
                self.deleteMino(self.block)
                self.block[1] -= 1
            self.block[1] += 1
            self.putMino(self.block)
        else:
            self.block = [i for i in self.mino]
            self.block[2] += 7

    def processInput(self, event):
        ret = False
        n = [i for i in self.mino]
        if event.key == K_ESCAPE:
            pygame.quit()
            sys.exit()
        elif event.key == K_UP and self.con: n[3] += 1
        elif event.key == K_DOWN and self.con: ret = True
        elif event.key == K_LEFT and self.con: n[0] -= 1
        elif event.key == K_RIGHT and self.con: n[0] += 1
        elif event.key == K_c: self.reset()
        elif event.key == K_f and self.canHold and self.con:
            self.canHold = False
            if self.hold == None:
                self.hold = [5, 21, self.mino[2], 0]
                n = [5, 21, 0, 0]
                n[2] = self.selectMino()
            else: self.hold, n = [5, 21, self.mino[2], 0], [i for i in self.hold]
            for x in range(5):
                for y in range(5): self.board_hold[x][y] = 15
            self.board_hold[2][2] = self.hold[2]
            for i in range(3):
                dx = self.minos[self.hold[2]][i + 1][0]
                dy = self.minos[self.hold[2]][i + 1][1]
                self.board_hold[2 + dx][2 + dy] = self.hold[2]
            for j in range(5): self.board_hold[j].reverse()
        elif event.key == K_q and self.con:
            n = [i for i in self.block]
            n[2] -= 7
            ret = True
        if n != self.mino:
            self.deleteMino(self.mino)
            if self.putMino(n): self.mino = [i for i in n]
            else: self.putMino(self.mino)
        return ret

    def minoDown(self):
        self.deleteMino(self.mino)
        self.mino[1] -= 1
        for i in range(len(self.attack)): self.attack[i] -= 1
        temp = []
        for i in self.attack:
            if i == 0: self.wall += 1
            if i > 0: temp.append(i)
        self.attack = [i for i in temp]
        if not self.putMino(self.mino):
            self.mino[1] += 1
            self.putMino(self.mino)
            self.fall.play()
            self.deleteLine()
            if self.wall > 0: self.makeWall()
            self.wall = 0
            self.canHold = True
            self.mino = [5, 21, 0, 0]
            self.mino[2] = self.selectMino()
            if not self.putMino(self.mino): self.gameOver()

    def gameOver(self):
        for x in range(1, 11):
            for y in range(1, 21):
                if self.board[x][y] != 0: self.board[x][y] = 15
        self.con = False

    def deleteLine(self):
    #tanaka
        y = 1
        self.pawer = 0
        while y < 28:
            flag = True
            for x in range(1, 11):
                if self.board[x][y] == 0: flag = False
            if flag:
                for j in range(y, 28):
                    for i in range(1, 11): self.board[i][j] = self.board[i][j + 1]
                self.pawer += 1
                continue
            y += 1
        if self.pawer > 0: self.chain += 1
        else: self.chain = 0
        if self.pawer == 4:
            if self.btb: self.pawer += 1
            self.btb = True
        elif self.pawer != 0:
            self.pawer -= 1
            self.btb = False
        self.flag = True
        for i in range(1, 11):
            if self.board[i][1] != 0:
                self.flag = False
                break
        if self.flag:
            self.allClear.play()
            self.pawer = 10
        elif self.chain > 0: self.line.play()
        if self.chain > 1:
            if self.chain < 9: self.pawer += self.chain // 2
            elif self.chain == 10: self.pawer += 4
            else: self.pawer += 5
        self.pawer, temp = self.pawer - len(self.attack), self.pawer
        for i in range(len(self.attack)):
            if i < temp: self.attack[i] = -1
        if self.pawer < 0: self.pawer = 0
        self.pawer, self.wall = self.pawer - self.wall, self.wall - self.pawer
        if self.pawer < 0: self.pawer = 0
        if self.wall < 0: self.wall = 0
        for _ in range(self.pawer): self.attack.append(15)

    def makeWall(self):
        n = random.randint(1, 10)
        for y in range(20, 0, -1):
            for x in range(1, 11):
                self.board[x][y + self.wall] = self.board[x][y]
                if y <= self.wall:
                    if x == n: self.board[x][y] = 0
                    else: self.board[x][y] = 15
        self.damage.play()
        
    def main(self):
        while not self.fin:
            if self.con:
                self.clock.tick(60)
                self.time += 1
                self.deleteMino(self.mino)
                self.putMino(self.mino)
                if self.time % 20 == 0: self.minoDown()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if(self.processInput(event)): self.time = -1
            if (not self.con) and self.se:
                pygame.mixer.music.pause()
                self.clear.play()
                self.se = False
                
            self.screen.fill((128, 192, 255))
            if self.con: self.hardDrop()
            self.loadBoard()
            pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if(self.processInput(event)): self.time = -1

game = Tetris()
game.main()
