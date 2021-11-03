from tkinter import *
from ShipLogic import *
from settings import *
from time import sleep

# Конфигурация окна
BSIZE = 20  # Размер клетки поля
FSTEP = 30  # Отступ между полями
WIDTH = FSTEP * 3 + BSIZE * S * 2
HEIGHT = FSTEP * 3 + BSIZE * S

root = Tk()
root.title('SeaBattle by Stiller')
root.geometry(f'{WIDTH}x{HEIGHT}')
root.resizable(height=False, width=False)

# Игровые глобальные переменные
CELLS = set()  # Клетки, отмеченные игроком на СВОЁМ поле
PL_SHIPS = set()
COMP_HIT_CELLS = set()  # Куда выстрелил компьютер

CAN_PRESS_RIGHT = True  # Можно ли удалять клетки

COMP_SHIPS = set()
COMP_FIRST = False  # Кто ходил первым?

PL_SCORE = 0
COMP_SCORE = 0
IS_GAME_OVER = False


def youWin():
    global PL_SCORE
    PL_SCORE += 1
    info('Ты выиграл!')
    gameOver()


def youLose():
    """При проигрыше показываем игроку корабли соперника, которые остались на доске"""
    global COMP_SCORE
    COMP_SCORE += 1
    info('Ты проиграл...')
    for ship in COMP_SHIPS:
        if not ship.isKilled():
            for c in ship:
                if not c in ship.wounded:
                    EBUTTONS[c.y][c.x].configure(bg=COMP_COLOR)
    gameOver()


def gameOver():
    """Поле компа деактивируется
    Кнопка "Сдаться" деактивируется
    Кнопка "Новая игра" активируется
    Панель счёта обновляется"""
    activateField(EBUTTONS, False)
    GIVE_UP.configure(state=DISABLED)
    NEW_GAME.configure(state=NORMAL)
    CHECK.configure(state=DISABLED)
    global IS_GAME_OVER
    IS_GAME_OVER = True
    updateScore()

def yourFieldPress(cords):
    """Нажатие в пределах поля игрока"""
    c = C(*cords)
    CELLS.add(c)
    PBUTTONS[c.y][c.x].configure(bg=PL_COLOR)


def oppFieldPress(cords):
    """Нажимаем на поле соперника"""
    c = C(*cords)
    GIVE_UP.configure(state=NORMAL)
    COMP_FIRST_B.configure(state=DISABLED)
    EBUTTONS[c.y][c.x].configure(state=DISABLED)
    if not shoot(COMP_SHIPS, EBUTTONS, c):
        compMove()
    else:
        for n in c.neibs(DIAG):
            EBUTTONS[n.y][n.x].configure(state=DISABLED, bg=CHECKED_COLOR)


def clear(field):
    """Визуально очистить клетки"""
    if field == PBUTTONS:
        col = PL_EMPTY
    else:
        col = COMP_EMPTY
    for line in field:
        for b in line:
            b.configure(bg=col)


def activateField(field, act=True):
    """Активировать или деактивировать все клетки данного поля"""
    for line in field:
        for B in line:
            if act:
                B.configure(state=NORMAL)
            else:
                B.configure(state=DISABLED)


class PButton(Button):
    """Кнопка поля игрока. Отдельный класс нужен для правого нажатия"""
    def __init__(self, cords, **kw):
        super().__init__(**kw)
        self.cords = C(*cords)

    def right_click(self, event):
        if self.cords in CELLS and CAN_PRESS_RIGHT:
            CELLS.remove(self.cords)
            PBUTTONS[self.cords.y][self.cords.x].configure(bg=PL_EMPTY)


def newGame():
    """Новая игра.
    Наше поле пустое.
    Соперник скрытно расставляет корабли.
    Активируется кнопка "расставил".
    Клетки соперника деактивированы.
    Наши клетки активированы.
    """
    global CELLS, COMP_SHIPS, CAN_PRESS_RIGHT, COMP_HIT_CELLS, IS_GAME_OVER
    # Очищаем своё поле
    clear(PBUTTONS)
    activateField(PBUTTONS, True)
    CAN_PRESS_RIGHT = True
    CELLS = set()
    IS_GAME_OVER = False
    info('Расставляй')

    # Поле соперника
    clear(EBUTTONS)
    activateField(EBUTTONS, act=False)
    COMP_SHIPS = setFleet()
    COMP_HIT_CELLS = set()

    # Меню
    NEW_GAME.configure(state=DISABLED)
    GIVE_UP.configure(state=DISABLED)
    COMP_FIRST_B.configure(state=DISABLED)
    CHECK.configure(state=NORMAL)
    AUTOSET.configure(state=NORMAL)
    #putRand()  # Убрать потом


def readyToStart():
    """Корабли расставлены.
    Надо выбрать, кто ходит первым"""
    COMP_FIRST_B.configure(state=NORMAL)
    activateField(EBUTTONS, act=True)


def checkField():
    """Проверяется, как игрок расставил корабли
    Если корабли расставились, правой кнопкой стирать клетки уже нельзя"""
    global PL_SHIPS, CAN_PRESS_RIGHT
    ships = checkUserCells(CELLS)
    if ships:
        activateField(PBUTTONS, False)
        info('Стреляй!')
        AUTOSET.configure(state=DISABLED)
        CHECK.configure(state=DISABLED)
        PL_SHIPS = ships
        readyToStart()
        CAN_PRESS_RIGHT = False


def putRand():
    """Нажата кнопка "Авто".
    Поле игрока визувльно очищается.
    Случайно расставляются корабли
    Обновляются множества клеток и кораблей"""
    clear(PBUTTONS)
    global CELLS, PL_SHIPS
    PL_SHIPS = setFleet()
    CELLS = shipsToSet(PL_SHIPS)
    for c in CELLS:
        PBUTTONS[c.y][c.x].configure(bg=PL_COLOR)


def compFirst():
    """Нажата кнопка "комп первый"
    Комплюктер ходит"""
    global COMP_FIRST
    COMP_FIRST = True
    compMove()
    GIVE_UP.configure(state=NORMAL)
    COMP_FIRST_B.configure(state=DISABLED)


def compMove():
    """shoot() возвращает флаг, в зависимости от которого комп
    продолжает ход"""
    c = smartShoot(PL_SHIPS, COMP_HIT_CELLS)
    COMP_HIT_CELLS.add(c)
    if shoot(PL_SHIPS, PBUTTONS, c):
        for n in c.neibs(DIAG):
            COMP_HIT_CELLS.add(n)
            PBUTTONS[n.y][n.x].configure(bg=CHECKED_COLOR)
        compMove()


def shipKilled(field, s):
    """Если корабль потоплен, надо отметить как проверенные все клетки вокруг него"""
    for c in s.neibs():
        field[c.y][c.x].configure(bg=CHECKED_COLOR, state=DISABLED)
        if field == PBUTTONS:
            COMP_HIT_CELLS.add(c)
    for c in s:
        #print(c)
        field[c.y][c.x].configure(bg=KILLED_COLOR)


def checkWin(ships, PL):
    """PL: флажок, обозначающий, кто ходил"""
    for s in ships:
        if not s.isKilled():
            return False
    if PL:
        youWin()
    else:
        youLose()
    return True


def shoot(ships, field, c):
    """Принимаются корабли, по которым стреляют,
    поле (список кнопок), которое будет модифицироваться,
    и координаты
    Возвращается Тру или Фолс в зависимости от попадания"""
    for s in ships:
        if c in s:
            s.hit(c)
            killed = s.isKilled()
            if killed:
                shipKilled(field, s)
                checkWin(ships, (field == EBUTTONS))
                return True
            else:
                field[c.y][c.x].configure(bg=WOUNDED_COLOR)
                return True
    if not IS_GAME_OVER:
        field[c.y][c.x].configure(bg=CHECKED_COLOR)


def info(text):
    """Вывод сообщений"""
    INFO.configure(text=text)


def updateScore():
    """Обновить текст в окне счёта"""
    SCORE.configure(text=f'Игрок: {PL_SCORE}; Комп: {COMP_SCORE}')

# Поля сообщений
INFO = Label()
INFO.place(x=FSTEP, y=FSTEP//3)

SCORE = Label()
SCORE.place(x=WIDTH-FSTEP-120, y=FSTEP//3)

# Клетки меню
CHECK = Button(command=checkField, bg=MENU_COLOR, text='Расставил!')
CHECK.place(x=FSTEP, y=FSTEP)

AUTOSET = Button(command=putRand, bg=MENU_COLOR, text='Авто')
AUTOSET.place(x=FSTEP+75, y=FSTEP)

COMP_FIRST_B = Button(command=compFirst, bg=MENU_COLOR, text='Ходить вторым')
COMP_FIRST_B.place(x=FSTEP+120, y=FSTEP)

GIVE_UP = Button(command=youLose, bg=MENU_COLOR, text='Сдаться')
GIVE_UP.place(x=WIDTH-FSTEP-130, y=FSTEP)

NEW_GAME = Button(command=newGame, bg=MENU_COLOR, text='Новая игра')
NEW_GAME.place(x=WIDTH-FSTEP-70, y=FSTEP)


# Player buttons
PBUTTONS = []
for y in range(S):
    PBUTTONS.append([])
    for x in range(S):
        b = PButton(cords=C(x, y), command=lambda cords=(x, y): yourFieldPress(cords), bg=PL_EMPTY)
        b.place(x=FSTEP + BSIZE * x, y=FSTEP * 2 + BSIZE * y, height=BSIZE, width=BSIZE)
        b.bind('<Button-3>', b.right_click)
        PBUTTONS[y].append(b)


EBUTTONS = []
for y in range(S):
    EBUTTONS.append([])
    for x in range(S):
        b = Button(command=lambda cords=(x, y): oppFieldPress(cords), bg=COMP_EMPTY)
        b.place(x=FSTEP * 2 + BSIZE * x + BSIZE * S, y=FSTEP * 2 + BSIZE * y, height=BSIZE, width=BSIZE)
        EBUTTONS[y].append(b)

updateScore()
newGame()

root.mainloop()
