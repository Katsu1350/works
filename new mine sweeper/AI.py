import numpy as np
class AI():
    def __init__(self):
        self.answer = []
        self.temp = []
        self.start = False
        self.step = True
    def main(self, lst, n):
        if not self.start:
            self.start = True
            self.answer.append([7,7,1])
        if not self.answer and self.step:
            self.step_1(lst)                    
        if not self.answer and not self.step:
            self.step = not self.step
            self.temp = []
            for i in range(16):
                for j in range(16):
                    if lst[i][j][1] == 0 or lst[i][j][1] == 2: continue
                    if lst[i][j][0] != 0:
                        cnt = 0
                        for x in [-1,0,1]:
                            if i + x < 0 or i + x > 15: continue
                            for y in [-1,0,1]:
                                if x == y == 0 or j + y < 0 or j + y > 15: continue
                                if lst[i+x][j+y][1] == 2:
                                    cnt += 1
                        if lst[i][j][0] == cnt:
                            self.temp.append([i,j])
            self.step_1(lst) 
        if not self.answer:
            index = []
            for pos in self.temp:
                cnt = 0
                for x in [-1,0,1]:
                    if pos[0] + x < 0 or pos[0] + x > 15: continue
                    for y in [-1,0,1]:
                        if x == y == 0 or pos[1] + y < 0 or pos[1] + y > 15: continue
                        if lst[pos[0]+x][pos[1]+y][1] == 0: cnt += 1
                if cnt != 0: index.append(cnt)
                else: index.append(10)
            if index and min(index) < 10:
                x = self.temp[index.index(min(index))][0]
                y = self.temp[index.index(min(index))][1]
                self.answer.append([x, y, 1])
        if n == 0:
            for i in range(16):
                for j in range(16):
                    if lst[i][j][1] == 0: self.answer.append([i, j, 1])
        if not self.answer:
            cnt = 0
            for i in range(16):
                for j in range(16):
                    if lst[i][j][1] == 0: cnt += 1
            p = cnt / n
            temp = [[[p, 0] for _ in range(16)] for _ in range(16)]
            for i in range(16):
                for j in range(16):
                    if lst[i][j][1] == 0 or lst[i][j][1] == 2: continue
                    if lst[i][j][0] != 0:
                        cnt1 = 0
                        cnt2 = 0
                        for x in [-1,0,1]:
                            if i + x < 0 or i + x > 15: continue
                            for y in [-1,0,1]:
                                if x == y == 0 or j + y < 0 or j + y > 15: continue
                                if lst[i+x][j+y][1] == 2:
                                    cnt1 += 1
                                flag = True
                                for pos in self.temp:
                                    if abs(i+x - pos[0]) < 1 and abs(j+y - pos[1]) < 1: flag = False
                                if lst[i+x][j+y][1] == 0 and flag:
                                    cnt2 += 1
                        if lst[i][j][0] != cnt1:
                            for x in [-1,0,1]:
                                if i + x < 0 or i + x > 15: continue
                                for y in [-1,0,1]:
                                    if x == y == 0 or j + y < 0 or j + y > 15: continue
                                    if lst[i+x][j+y][1] == 0 and cnt2 != 0:
                                        temp[i+x][j+y][1] += 1
                                        if temp[i+x][j+y][0] == p: temp[i+x][j+y][0] = 0
                                        temp[i+x][j+y][0] += (lst[i][j][0] - cnt1) / cnt2
            
            num = 10
            for i in range(16):
                for j in range(16):
                    if lst[i][j][1] != 0: continue
                    if temp[i][j][1] > 0: temp[i][j][0] /= temp[i][j][1]
                    if temp[i][j][0] <= num:
                        num = temp[i][j][0]
                        answer = [i, j, 1]
            self.answer.append(answer)
        if self.answer: return self.answer.pop()

    def step_1(self, lst):
        self.step = not self.step
        for i in range(16):
            for j in range(16):
                if lst[i][j][1] == 0 or lst[i][j][1] == 2: continue
                if lst[i][j][0] != 0:
                    cnt = 0
                    for x in [-1,0,1]:
                        if i + x < 0 or i + x > 15: continue
                        for y in [-1,0,1]:
                            if x == y == 0 or j + y < 0 or j + y > 15: continue
                            flag = False
                            for pos in self.temp:
                                if abs(i+x - pos[0]) <= 1 and abs(j+y - pos[1]) <= 1:
                                    flag = True
                                    break
                            if flag and lst[i+x][j+y][1] == 0: continue
                            if lst[i+x][j+y][1] == 0 or lst[i+x][j+y][1] == 2: cnt += 1
                    if lst[i][j][0] == cnt:
                        for x in [-1,0,1]:
                            if i + x < 0 or i + x > 15: continue
                            for y in [-1,0,1]:
                                if x == y == 0 or j + y < 0 or j + y > 15: continue
                                flag = False
                                for pos in self.temp:
                                    if abs(i+x - pos[0]) <= 1 and abs(j+y - pos[1]) <= 1:
                                        flag = True
                                        break
                                if flag and lst[i+x][j+y][1] == 0: continue
                                if lst[i+x][j+y][1] == 0 and not [i+x, j+y, 3] in self.answer: self.answer.append([i+x, j+y, 3])
