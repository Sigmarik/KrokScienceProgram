import pygame
import time
from math import *
from random import randint
import os
from subprocess import check_output
import threading

pygame.init()

def run_keyboard():
    os.system("osk")

font = pygame.font.Font('arial.otf', 24)

th = threading.Thread(target=run_keyboard, args=())
#th.start()

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
HLT = imload('assets/selection.bmp')

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

class line:
    a = 0
    b = 0
    c = 0
    #ax + by + c = 0
    def __init__(self, A, B):
        self.a = A.y - B.y
        self.b = B.x - A.x
        self.c = A.x * B.y - B.x * A.y
    def insec(A, B):
        A1 = A.a
        A2 = B.a
        B1 = A.b
        B2 = B.b
        C1 = A.c
        C2 = B.c
        if B1*A2 - B2*A1 and A1:
            y = (C2*A1 - C1*A2) / (B1*A2 - B2*A1)
            x = (-C1 - B1*y) / A1
            return vert([x, y])
        elif B1*A2 - B2*A1 and A2:
            y = (C2*A1 - C1*A2) / (B1*A2 - B2*A1)
            x = (-C2 - B2*y) / A2
            return vert([x, y])
        else:
            return vert([0, 0])
    def proj(self, P):
        #-b; a
        #a; b
        ort = line(P, P + vert([self.a, self.b]))
        answ = ort.insec(self)
        #pygame.draw.circle(scr, [255, 255, 255], answ.get_arr(), 3)
        return answ

def blit_centred(scr, img, pos):
    H, W = img.get_height(), img.get_width()
    scr.blit(img, (pos - vert([W / 2, H / 2])).get_arr())

class ball:
    pos = vert([0, 0])
    mass = 10
    typ = 'static'
    vel = vert((0, 0))
    constant_acceleration = vert([0, 0])
    highlight = False
    def __init__(self, pos, typ='weight', mass=1):
        self.pos = pos
        self.mass = 10
        self.typ = typ
    def update(self):
        global gravity
        if self.typ != 'static':
            if self.typ == 'weight':
                self.vel = self.vel + vert([0, gravity]) * delta_time
                self.vel = self.vel + self.vel * delta_time * -0.1
            self.pos = self.pos + self.vel * delta_time
        if self.pos.y >= 10000:
            remove_object(objects.index(self))
    def draw(self, scr):
        if self.pos.y <= 3000:
            if self.typ == 'static':
                img = STATIC
            elif self.typ == 'weight':
                img = WEIGHT
            if self.highlight:
                blit_centred(scr, HLT, self.pos)
                #pygame.draw.circle(scr, [255, 255, 255], self.pos.get_arr(), 10)
            blit_centred(scr, img, self.pos)
    def dist(self, point):
        return (self.pos - point).len() - 6

class spring:
    K = 0.1
    X_zero = 0
    A = 0
    B = -1
    highlight = False
    def __init__(self, A, B, K=0.1):
        self.K = K
        self.X_zero = (objects[A].pos - objects[B].pos).len()
        self.A = A
        self.B = B
    def update(self):
        blA = objects[self.A]
        blB = objects[self.B]
        delta = (blB.pos - blA.pos).u()
        dX = (blA.pos - blB.pos).len() - self.X_zero
        objects[self.A].vel = blA.vel + delta * dX * self.K * delta_time / blA.mass
        objects[self.B].vel = blB.vel - delta * dX * self.K * delta_time / blB.mass
    def draw(self, scr):
        blA = objects[self.A]
        blB = objects[self.B]
        delta = (blB.pos - blA.pos).u()
        dX = (blA.pos - blB.pos).len() - self.X_zero
        color = [max(0, min(255, 127 + int(dX))), 127, 127]
        if self.highlight:
            pygame.draw.line(scr, [255, 255, 255], blA.pos.get_arr(), blB.pos.get_arr(), 5)
        pygame.draw.line(scr, color, blA.pos.get_arr(), blB.pos.get_arr(), 3)
    def dist(self, P):
        blA = objects[self.A]
        blB = objects[self.B]
        ln = line(blA.pos, blB.pos)
        projection = ln.proj(P)
        #print(((proj - blA.pos).len() + (proj - blB.pos).len(),  (blA.pos - blB.pos).len()))
        if (projection - blA.pos).len() + (projection - blB.pos).len() <= (blA.pos - blB.pos).len() + 5:
            answ = (projection - P).len()
        else:
            answ = min((P - blA.pos).len(), (P - blB.pos).len())
        #print(answ)
        return answ

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

class number_cell(UI):
    value = ''
    is_active = False
    def __init__(self, binding):
        self.value = ''
        self.is_active = False
    def draw(self):
        (font.render)
def nearest_ball(P):
    minn = 9999999999
    index = 0
    for i in range(len(objects)):
        obj = objects[i]
        D = obj.dist(P)
        if type(obj) == ball and D < minn:
            index = i
            minn = D
    return [index, minn]

def nearest_spring(P):
    minn = 10 ** 9
    index = 0
    for i, obj in enumerate(objects):
        D = obj.dist(P)
        if type(obj) == spring and D < minn:
            index = i
            minn = D
    return index, minn

def nearest_object(P):
    minn = 10 ** 9
    index = 0
    for i, obj in enumerate(objects):
        D = obj.dist(P)
        if D < minn:
            index = i
            minn = D
    return index, minn

def remove_object(ind):
    removers = []
    for i in list(range(len(objects)))[::-1]:
        obj = objects[i]
        if type(obj) == spring:
            if obj.A == ind or obj.B == ind:
                removers.append(i)
            else:
                if obj.A > ind:
                    objects[i].A -= 1
                if obj.B > ind:
                    objects[i].B -= 1
    for rem in removers:
        remove_object(rem)
    objects.pop(ind)

def add_num(num):
    _=0

kg = True
info = pygame.display.Info()
SZX, SZY = info.current_w, info.current_h
scr = pygame.display.set_mode([SZX, SZY], pygame.FULLSCREEN)
time_stop = 0

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
""", logo='play.bmp'))
UIs.append(button(rect=[0, SZY - 40, 80, 40], color=[100, 100, 150], on_press="""
global curent_tool
curent_tool = (curent_tool + 1) % 3
self.logo_img = imload('assets/mode' + str(curent_tool) + '.bmp')
""", logo='mode0.bmp'))
UIs.append(button(rect=[81, SZY - 40, 80, 40], color=[100, 100, 150], on_press="""
global inventory_slot
inventory_slot = (inventory_slot + 1) % 3
self.logo_img = imload('assets/inventory' + str(inventory_slot) + '.bmp')
""", logo='inventory0.bmp'))

tm = time.monotonic()
curent_spring = None
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
        if event.type == pygame.MOUSEBUTTONDOWN and (not rs):
            if curent_tool == 0:
                if inventory_slot == 0:
                    objects.append(ball(vert(mpos), 'static'))
                if inventory_slot == 1:
                    objects.append(ball(vert(mpos), 'weight'))
                if inventory_slot == 2:
                    curent_spring = nearest_ball(vert(mpos))[0]
                    #print(curent_spring)
            if curent_tool == 1:
                if len(objects) > 0:
                    no = nearest_object(vert(mpos))[0]
                    #print(objects[no].dist(vert(mpos)))
                    remove_object(no)
            if curent_tool == 2:
                if len(objects) > 0:
                    no = nearest_spring(vert(mpos))[0]
                    print(objects[no].dist(vert(mpos)))
        if event.type == pygame.MOUSEBUTTONUP and (not rs):
            if curent_tool == 0:
                if inventory_slot == 2:
                    nb = nearest_ball(vert(mpos))[0]
                    #print(nb)
                    if nb != curent_spring and nearest_spring != None:
                        objects.append(spring(curent_spring, nb, K=1000))
                    curent_spring = None
    for i in range(len(objects)):
        objects[i].highlight = False
        nr = nearest_object(vert(mpos))
    if curent_spring != None:
        nb = nearest_ball(vert(mpos))[0]
        objects[nb].highlight = True
        objects[curent_spring].highlight = True
        pygame.draw.line(scr, [255, 255, 255], objects[nb].pos.get_arr(), objects[curent_spring].pos.get_arr(), 3)
    for obj in objects:
        if type(obj) == spring:
            obj.update()
            obj.draw(scr)
    for obj in objects:
        if type(obj) == ball:
            obj.update()
            obj.draw(scr)
    for U in UIs:
        U.draw()
    pygame.display.update()
pygame.quit()
