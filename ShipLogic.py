from collections import namedtuple
from random import randint, choice


class C(namedtuple('C', 'x y')):
    """Класс координат клетки"""
    def __add__(self, oth):
        """Прибавляем к координатам значения вектора для нахождения соседей"""
        return C(self.x + oth.x, self.y + oth.y)

    def neibs(self, vecs):
        """Находим соседей по DIAG или ORTH"""
        out = set()
        for vec in vecs:
            c = self + vec
            if c.onBoard():
                out.add(c)
        return out

    def onBoard(self):
        """А эта клетка вообще на поле?"""
        for e in self:
            if e < 0 or e >= S:
                return False
        return True


class ShipWreck(Exception):
    pass


ORTH = (C(1, 0), C(0, 1), C(-1, 0), C(0, -1))
DIAG = (C(1, 1), C(1, -1), C(-1, -1), C(-1, 1))

# Сторона квадратного поля
S = 8
# Длина наибольшего корабля
L = 4

# =======================
n = 1
# Количество клеток во флотилии
cellN = 0
SHIPLIST = []
# Количество кораблей во флотилии
ShipN = 0
for s in range(L, 0, -1):
    cellN += n * s
    SHIPLIST.append((s, n))
    ShipN += n
    n += 1


# =======================


def randC():
    """Случайная клетка в пределах поля"""
    return C(randint(0, S-1), randint(0, S-1))


def freeCells(occ):
    poss = []
    for y in range(S):
        for x in range(S):
            c = C(x, y)
            if c not in occ:
                poss.append(c)
    return poss


def randShoot(occ):
    """Случвйнвя клетка для выстрела из незанятых"""
    poss = freeCells(occ)
    if poss:
        return choice(poss)
    else:
        return None

class Ship(set):
    """Кораблик в виде множества входящих в него координат клеток"""
    def __init__(self, n=0, occ=set(), cells=None):
        super().__init__()
        self.wounded = set()
        if cells:
            self.update(cells)
        else:
            start = randC()
            vec = choice(ORTH)
            for i in range(n):
                self.add(start)
                start += vec
            # print(self)
            self.initLoc = set(self)
            if not self.onBoard() or not self.noCollisions(occ):
                # print('!!!')
                self.findPlace(occ)

    def goBack(self):
        """Возврат корвбля в исходное положение"""
        self.clear()
        self.update(self.initLoc)

    def move(self, vec):
        """Сдвигаем весь корабль по вектору"""
        new = set()
        for t in self:
            new.add(t + vec)
        self.clear()
        self.update(new)

    def onBoard(self):
        """Все ли клетки корабля сейчас на поле?"""
        for c in self:
            if not c.onBoard():
                return False
        return True

    def noCollisions(self, occ):
        """Проверяем, не пересекается ли множество
        клеток корабля с запрещёнными клетками"""
        # print(self & occ)
        return not self & occ

    def findPlace(self, occ):
        for vec in ORTH:
            for i in range(S - 1):
                self.move(vec)
                # print(f'V: {vec}')
                if self.onBoard() and self.noCollisions(occ):
                    return
            self.goBack()
        raise ShipWreck

    def neibs(self):
        """Находим все соседние с кораблём клетки"""
        out = set()
        for c in self:
            out.update(c.neibs(ORTH))
            out.update(c.neibs(DIAG))
        return out
    
    def isKilled(self):
        return self.wounded == self

    def hit(self, c):
        self.wounded.add(c)


def setFleet():
    """Расстановка кораблей компьютером"""
    while True:
        try:
            ships = []
            occ = set()
            # L: length of the biggest ship
            n = 1
            for s in range(L, 0, -1):
                # print(s)
                for i in range(n):
                    ship = Ship(s, occ)
                    ships.append(ship)
                    occ.update(ship.neibs())
                    occ.update(ship)
                n += 1
            return ships
        except ShipWreck:
            continue


def checkUserCells(cells):
    """Проверка правильности расстановки кораблей игроком.
    Если всё правильно, возвращает множество кораблей
    класса Ship. Если допущена ошибка - None или False
    cells should be a sequence of C()s"""
    if len(cells) != cellN:
        return False
    for c in cells:
        if c.neibs(DIAG) & cells:
            return False

    sList = list(SHIPLIST)
    ships = []
    addedCells = set()

    for s, n in sList:  # s - size of ship. n - number of ships
        for i in range(n):
            for c in cells:
                if c not in addedCells:
                    for vec in ORTH:
                        new = c
                        line = set()
                        for j in range(s):
                            if new in cells and new not in addedCells:
                                line.add(new)
                            else:
                                break
                            new += vec
                        if len(line) == s:
                            ships.append(Ship(cells=line))
                            addedCells.update(line)
    if len(ships) == ShipN:
        return ships
    else:
        return None


def shipsToSet(ships):
    """Принимает корабли и возвращает входящие в них клетки"""
    out = set()
    for ship in ships:
        out.update(ship)
    return out


def smartShoot(pl_ships, hit_cells):
    good_moves = []
    for ship in pl_ships:
        if ship.wounded and not ship.isKilled():
            for c in ship.wounded:
                for neib in c.neibs(ORTH):
                    if neib.onBoard() and not neib in hit_cells:
                        good_moves.append(neib)
    if not good_moves:
        return randShoot(hit_cells)
    return choice(good_moves)