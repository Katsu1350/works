class Iter():
    def __init__(self, s):
        self.s = s
        self.num = -1
    def next(self):
        self.num += 1
        return self.s[self.num]
    def hasNext(self):
        if self.num + 1 < len(self.s):
            return True
        else:
            return False
    def seeNext(self):
        return self.s[self.num + 1]
