import pygame
from pygame.locals import *
import numpy as np
import sys

class NewMineSweeper():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("new! mine sweeper")
        self.screen = pygame.display.set_mode((545, 625))
        self.img = pygame.image.load("img.png")
        self.board = [[[0,0] for _ in range(16)] for _ in range(16)]
        self.start = None
        self.loop = True
        self.turn = 0
        self.numberOfFlag = 40
        self.numberOfMine = 40
    
    def reset(self):
        self.board = [[[0,0] for _ in range(16)] for _ in range(16)]
        self.start = None
        self.loop = True
        self.win = True
        self.numberOfFlag = 40
        self.numberOfMine = 40
        self.main()

    def click(self, x, y, button):
        switch = False
        if button == 1:
            if self.board[x][y][1] == 1:
                switch = True
                for i in [-1, 0, 1]:
                    if i + x < 0 or i + x > 15: continue
                    for j in [-1, 0, 1]:
                        if i == j == 0 or j + y < 0 or j + y > 15: continue
                        if self.board[x+i][y+j][1] != 1:
                            self.leftClick(x+i , y+j)
                            switch = False
            else: self.leftClick(x , y)
            self.turn += 1
            if switch: self.turn -= 1
        elif button == 3 and self.board[x][y][1] == 0 and self.numberOfFlag > 0:
            self.board[x][y][1] = 2
            self.numberOfFlag -= 1
            if self.board[x][y][0] == 9:
                self.numberOfMine -= 1
        elif button == 3 and self.board[x][y][1] == 2:
            self.board[x][y][1] = 0
            self.numberOfFlag += 1
            if self.board[x][y][0] == 9:
                self.numberOfMine += 1
        
        if not self.start:
            self.start = pygame.time.get_ticks()
            temp = self.numberOfMine
            while temp > 0:
                r = np.random.randint(256)
                if self.board[r%16][r//16][0] == 9 or self.board[r%16][r//16][1] != 0 or (abs(x-r%16) <= 1 and abs(y-r//16) <= 1): continue
                self.board[r%16][r//16][0] = 9
                temp -= 1
            for i in range(16):
                for j in range(16):
                    if self.board[i][j][0] == 9: continue
                    cnt = 0
                    for a in [-1,0,1]:
                        if i + a < 0 or i + a > 15: continue
                        for b in [-1,0,1]:
                            if a == b == 0 or j + b < 0 or j + b > 15: continue
                            if self.board[i+a][j+b][0] == 9: cnt += 1
                    self.board[i][j][0] = cnt
            self.autClick(x, y)
        
        if self.turn % 5 == 0 and button == 1:
            for i in range(16):
                for j in range(16):
                    if self.board[i][j][1] == 0: self.board[i][j][0] = 0
            
            temp = self.numberOfMine
            while temp > 0:
                r = np.random.randint(256)
                if self.board[r%16][r//16][0] == 9 or self.board[r%16][r//16][1] != 0: continue
                self.board[r%16][r//16][0] = 9
                temp -= 1
        
            for i in range(16):
                for j in range(16):
                    if self.board[i][j][0] == 9: continue
                    cnt = 0
                    for x in [-1,0,1]:
                        if i + x < 0 or i + x > 15: continue
                        for y in [-1,0,1]:
                            if x == y == 0 or j + y < 0 or j + y > 15: continue
                            if self.board[i+x][j+y][0] == 9: cnt += 1
                    self.board[i][j][0] = cnt
        
    def leftClick(self, x, y):
        if self.board[x][y][1] != 2:
            self.board[x][y][1] = 1
            if self.board[x][y][0] == 9:
                self.loop = False
                for i in range(16):
                    for j in range(16):
                        if self.board[i][j][0] != 9:
                            self.board[i][j][1] = 2
                            self.board[i][j][0] = 11
                        else: self.board[i][j][1] = 1
                return
            if self.start: self.autClick(x, y)
    
    def autClick(self, x, y):
        cnt = 0
        for i in [-1,0,1]:
            if x + i < 0 or x + i > 15: continue
            for j in [-1,0,1]:
                if x == y == 0 or y + j < 0 or y + j > 15: continue
                if self.board[i+x][j+y][0] == 9: cnt += 1
        if cnt == 0:
            for i in [-1,0,1]:
                if x + i < 0 or x + i > 15: continue
                for j in [-1,0,1]:
                    if x == y == 0 or y + j < 0 or y + j > 15: continue
                    if self.board[x+i][y+j][1] == 0: self.leftClick(x+i, y+j)
    
    def check(self):
        cnt = 0
        for i in range(16):
            for j in range(16):
                if self.board[i][j][1] == 1: cnt += 1
        if cnt == 216:
            self.screen.blit(self.img, (244, 25), (210, 120, 60, 60))
            while True:
                for i in range(16):
                    for j in range(16):
                        if self.board[i][j][1] == 2:
                            if self.board[i][j][0] != 11:
                                self.screen.blit(self.img, (i*31+25, j*31+105), (120, 30, 30, 30))
                            else: self.screen.blit(self.img, (i*31+25, j*31+105), (180, 00, 30, 30))
                        elif self.board[i][j][1] == 1:
                            self.screen.blit(self.img, (i*31+25, j*31+105), (self.board[i][j][0]%6*30, self.board[i][j][0]//6*30, 30, 30))
                            if self.board[i][j][0] == 0:
                                self.screen.blit(self.img, (i*31+25, j*31+105), (180, 0, 30, 30))
                        elif self.board[i][j][1] == 0:
                            self.screen.blit(self.img, (i*31+25, j*31+105), (0, 0, 30, 30))
                pygame.display.update()  
                for event in pygame.event.get():
                        if event.type == QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.MOUSEBUTTONUP:
                            pos = pygame.mouse.get_pos()
                            if pos[0] >= 244 and pos[0] <= 304 and pos[1] >= 25 and pos[1] <= 85: self.reset()
    
    def main(self):
        time = 0
        while self.loop:
            if self.start: time = (pygame.time.get_ticks() - self.start) // 1000
            if time >= 999: time = 999
            self.screen.fill((223,223,223))
            self.screen.blit(self.img, (401, 25), (time//100%5*30, time//500*60+60, 30, 60))
            time = time % 100
            self.screen.blit(self.img, (431, 25), (time//10%5*30, time//50*60+60, 30, 60))
            time = time % 10
            self.screen.blit(self.img, (461, 25), (time%5*30, time//5*60+60, 30, 60))
            self.screen.blit(self.img, (244, 25), (210, 0, 60, 60))
            self.screen.blit(self.img, (55, 25), (self.numberOfFlag//10%5*30, self.numberOfFlag//50*60+60, 30, 60))
            temp = self.numberOfFlag % 10
            self.screen.blit(self.img, (85, 25), (temp%5*30, temp//5*60+60, 30, 60))
            pygame.draw.rect(self.screen, (150,150,150), Rect(24, 104, 497, 497))
            for i in range(16):
                for j in range(16):
                    if self.board[i][j][1] == 2:
                        if self.board[i][j][0] != 11:
                            self.screen.blit(self.img, (i*31+25, j*31+105), (120, 30, 30, 30))
                        else: self.screen.blit(self.img, (i*31+25, j*31+105), (180, 00, 30, 30))
                    elif self.board[i][j][1] == 1:
                        self.screen.blit(self.img, (i*31+25, j*31+105), (self.board[i][j][0]%6*30, self.board[i][j][0]//6*30, 30, 30))
                        if self.board[i][j][0] == 0:
                            self.screen.blit(self.img, (i*31+25, j*31+105), (180, 0, 30, 30))
                    elif self.board[i][j][1] == 0:
                        self.screen.blit(self.img, (i*31+25, j*31+105), (0, 0, 30, 30))

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if pos[0] >= 244 and pos[0] <= 304 and pos[1] >= 25 and pos[1] <= 85: self.reset()
                    x = (pos[0] - 25) // 31
                    y = (pos[1] - 105) // 31
                    if x >= 0 and x <= 15 and y >= 0 and y <= 15:
                        self.click(x, y, event.button)
            
            pos = pygame.mouse.get_pos()
            x = (pos[0] - 25) // 31
            y = (pos[1] - 105) // 31
            if x >= 0 and x <= 15 and y >= 0 and y <= 15: 
                self.screen.blit(self.img, (x*31+25, y*31+105), (150, 30, 30, 30))
            self.check()

            pygame.display.update()    
        self.gameOver()
        
    def gameOver(self):
        while True:
            for i in range(16):
                for j in range(16):
                    self.screen.blit(self.img, (i*31+25, j*31+105), (self.board[i][j][0]%6*30, self.board[i][j][0]//6*30, 30, 30))
                    if self.board[i][j][1] == 2:
                        self.screen.blit(self.img, (i*31+25, j*31+105), (180, 0, 30, 30))
            self.screen.blit(self.img, (244, 25), (210, 60, 60, 60))
            pygame.display.update()  
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if pos[0] >= 244 and pos[0] <= 304 and pos[1] >= 25 and pos[1] <= 85: self.reset()

game = NewMineSweeper()
game.main()