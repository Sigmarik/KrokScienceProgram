import pygame
import time
from math import *
from random import randint

balls = []
springs = []
gravity = 98

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
    def draw(self):
        blA = balls[self.A]
        blB = balls[self.B]
        delta = (blB.pos - blA.pos).u()
        dX = (blA.pos - blB.pos).len() - self.X_zero
        color = [max(0, min(255, 127 + int(dX))), 127, 127]
        pygame.draw.line(scr, color, blA.pos.get_arr(), blB.pos.get_arr(), 3)

kg = True
SZX, SZY = 800, 800
scr = pygame.display.set_mode([SZX, SZY])
time_stop = 1

tm = time.monotonic()
while kg:
    TM = time.monotonic()
    delta_time = (TM - tm) * time_stop
    tm = TM
    scr.fill([50, 100, 50])
    mpos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            kg = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            #print(mpos, vert(mpos).get_arr())
            if event.button == 1:
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
        spr.draw()
    for bl in balls:
        bl.update()
        bl.draw(scr)
    pygame.display.update()
pygame.quit()
