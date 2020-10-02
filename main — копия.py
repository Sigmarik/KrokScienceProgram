import pygame
import time
from math import *
from random import randint

pygame.init()

objects = []
#balls = []
#springs = []
gravity = 980
UIs = []

def imload(name, pos=[0, 0]):
    img = pygame.image.load(name)
    if pos != None:
        img.set_colorkey(img.get_at(pos))
    return img

STATIC = imload('assets/rest.bmp')
WEIGHT = imload('assets/weight.bmp')

class vert:
    x = 0
    y = 0
    def __init__(self, arr):
        self.x, self.y = list(arr)
        #print(x, y)
    def __getitem__(self, ind):
        return list([self.x, self.y])[ind]
    def __add__(A, B):
        return vert([A.x + B.x, A.y + B.y])
    def __mul__(A, B):
        return vert([A.x * B, A.y * B])
    def len(A):
        return sqrt(A.x * A.x + A.y * A.y)
    def __sub__(A, B):
        return A + (B * -1)
    def __truediv__(A, B):
        return A * (1 / B)
    def u(self):
        if self.len() != 0:
            return self / self.len()
        else:
            return vert([1, 0])
    def get_arr(self):
        return [int(self.x), int(self.y)]

def blit_centred(scr, img, pos):
    H, W = img.get_height(), img.get_width()
    scr.blit(img, (pos - vert([W / 2, H / 2])).get_arr())

class ball:
    pos = vert([0, 0])
    mass = 10
    typ = 'static'
    vel = vert((0, 0))
    constant_acceleration = vert([0, 0])
    def __init__(self, pos, typ='weight', mass=1):
        self.pos = pos
        self.mass = 10
        self.typ = typ
    def update(self):
        global gravity
        if self.typ != 'static':
            if self.typ == 'weight':
                self.vel = self.vel + vert([0, gravity]) * delta_time
            self.pos = self.pos + self.vel * delta_time
    def draw(self, scr):
        if self.typ == 'static':
            img = STATIC
        elif self.typ == 'weight':
            img = WEIGHT
        blit_centred(scr, img, self.pos)

class spring:
    K = 0.1
    X_zero = 0
    A = 0
    B = -1
    def __init__(self, A, B, K=0.1):
        self.K = K
        self.X_zero = (balls[A].pos - balls[B].pos).len()
        self.A = A
        self.B = B
    def update(self):
        blA = balls[self.A]
        blB = balls[self.B]
        delta = (blB.pos - blA.pos).u()
        dX = (blA.pos - blB.pos).len() - self.X_zero
        balls[self.A].vel = blA.vel + delta * dX * self.K * delta_time / blA.mass
        balls[self.B].vel = blB.vel - delta * dX * self.K * delta_time / blB.mass
    def draw(self, scr):
        blA = balls[self.A]
        blB = balls[self.B]
        delta = (blB.pos - blA.pos).u()
        dX = (blA.pos - blB.pos).len() - self.X_zero
        color = [max(0, min(255, 127 + int(dX))), 127, 127]
        pygame.draw.line(scr, color, blA.pos.get_arr(), blB.pos.get_arr(), 3)

class UI:
    rect = [0, 0, 0, 0]
    def draw(self):
        _=0
    def update(self):
        _=0

class button(UI):
    press_code = ''
    release_code = ''
    logo_img = None
    is_pressed = False
    color = [0, 0, 0]
    def __init__(self, rect=[0, 0, 0, 0], color=[0, 0, 0], on_press='', on_release='', logo=None):
        self.press_code = on_press
        self.release_code = on_release
        self.color = color.copy()
        self.rect = rect.copy()
        if type(logo) == type(pygame.Surface([100, 100])):
            self.logo_img = logo.copy()
        elif type(logo) == type('abcd'):
            self.logo_img = imload('assets/' + logo)
        elif logo == None:
            self.logo_img = logo
    def press(self):
        self.is_pressed = True
        exec(self.press_code)
    def release(self):
        self.is_pressed = False
        exec(self.release_code)
    def on_mouse(self, action):
        mps = pygame.mouse.get_pos()
        res = False
        if self.rect[0] <= mps[0] <= self.rect[0] + self.rect[2] and self.rect[1] <= mps[1] <= self.rect[1] + self.rect[3]:
            res = True
            if action.type == pygame.MOUSEBUTTONDOWN:
                self.press()
        if action.type == pygame.MOUSEBUTTONUP and self.is_pressed:
            self.release()
        return res
    def draw(self):
        mps = pygame.mouse.get_pos()
        if self.is_pressed:
            col = [int(x / 2) for x in self.color]
        else:
            if self.rect[0] <= mps[0] <= self.rect[0] + self.rect[2] and self.rect[1] <= mps[1] <= self.rect[1] + self.rect[3]:
                col = [int(x / 1.5) for x in self.color]
            else:
                col = self.color.copy()
        pygame.draw.rect(scr, [255, 255, 255], self.rect, 3)
        pygame.draw.rect(scr, col, self.rect)
        if self.logo_img != None:
            blit_centred(scr, self.logo_img, vert([self.rect[0] + self.rect[2] // 2, self.rect[1] + self.rect[3] // 2]))

class number_panel:
    index = 0
    def __init__(self, cell):
        global UIs, SZX, SZY
        self.index = len(UIs)
        UIs.append(button(rect=[SZX // 2 - 100, SZY // 2 - 150, 20, 20], color=[100, 100, 100], on_press=""""""))

class number_cell(UI):
    value = ''
    is_active = False

kg = True
info = pygame.display.Info()
SZX, SZY = info.current_w, info.current_h
scr = pygame.display.set_mode([SZX, SZY], pygame.FULLSCREEN)
time_stop = 1

curent_tool = 0
# 0 - place
# 1 - remove
# 2 - edit
inventory_slot = 0

UIs.append(button(rect=[0, 0, 50, 25], color=[150, 100, 100], on_press="""global kg
kg = False""", logo='quit.bmp'))
UIs.append(button(rect=[0, 26, 50, 25], color=[100, 150, 100], on_press="""
global time_stop
time_stop = (time_stop + 1) % 2
if time_stop == 0:
    self.logo_img = imload('assets/play.bmp')
else:
    self.logo_img = imload('assets/pause.bmp')
""", logo='pause.bmp'))
UIs.append(button(rect=[0, SZY - 40, 80, 40], color=[100, 100, 150], on_press="""
global curent_tool
curent_tool = (curent_tool + 1) % 3
self.logo_img = imload('assets/mode' + str(curent_tool) + '.bmp')
""", logo='mode0.bmp'))

tm = time.monotonic()
while kg:
    TM = time.monotonic()
    delta_time = (TM - tm) * time_stop
    tm = TM
    scr.fill([50, 100, 50])
    mpos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        rs = False
        for U in UIs:
            if U.on_mouse(event):
                rs = True
        if event.type == pygame.QUIT:
            kg = False
        if event.type == pygame.MOUSEBUTTONDOWN and not rs:
            #print(mpos, vert(mpos).get_arr())
            if event.button == 1:
                if curent_tool 
                balls.append(ball(vert(mpos), 'static'))
            if event.button == 3:
                balls.append(ball(vert(mpos), 'weight', mass=randint(1, 20)))
            if len(balls) >= 2:
                springs.append(spring(len(balls) - 2, len(balls) - 1, K=100))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                time_stop = (time_stop + 1) % 2
    for spr in springs:
        spr.update()
        spr.draw(scr)
    for bl in balls:
        bl.update()
        bl.draw(scr)
    for U in UIs:
        U.draw()
    pygame.display.update()
pygame.quit()
