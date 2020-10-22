import pygame
import time
from math import *
from random import randint
import os
from subprocess import check_output
import threading

WORLD_CONSTANTS = [980, 0.1]

pygame.init()

def run_keyboard():
    os.system("osk")

font = pygame.font.Font('arial.otf', 24)
font_small = pygame.font.Font('arial.otf', 10)

th = threading.Thread(target=run_keyboard, args=())
#th.start()

objects = {}
#balls = []
#springs = []
gravity = 980
UIs = []
active_string = None
editable_object = None
curent_graph = None
indexes_to_remove = 0

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
        if self.mass == 0:
            self.mass = 0.1
        if self.typ != 'static':
            if self.typ == 'weight':
                self.vel = self.vel + vert([0, WORLD_CONSTANTS[0]]) * delta_time
                self.vel = self.vel + self.vel * delta_time * -WORLD_CONSTANTS[1]
            self.pos = self.pos + self.vel * delta_time
        else:
            self.vel = vert([0, 0])
        #if self.pos.y >= 10000:
        #    remove_object(objects.index(self))
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
    TForce = 0
    A = 0
    B = -1
    highlight = False
    def __init__(self, A, B, K=0.1):
        self.K = K
        self.X_zero = (objects[A].pos - objects[B].pos).len()
        self.A = A
        self.B = B
        self.TForce = 0
    def update(self):
        try:
            blA = objects[self.A]
            blB = objects[self.B]
            delta = (blB.pos - blA.pos).u()
            dX = (blA.pos - blB.pos).len() - self.X_zero
            objects[self.A].vel = blA.vel + delta * dX * self.K * delta_time / blA.mass
            objects[self.B].vel = blB.vel - delta * dX * self.K * delta_time / blB.mass
            self.TForce = (delta * dX).len()
        except ZeroDivisionError:
            _=0
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
        global font
        self.press_code = on_press
        self.release_code = on_release
        self.color = color.copy()
        self.rect = rect.copy()
        if type(logo) == type(pygame.Surface([100, 100])):
            self.logo_img = logo.copy()
        elif type(logo) == type('abcd'):
            try:
                self.logo_img = imload('assets/' + logo)
            except:
                self.logo_img = font.render(logo, 1, [0, 0, 0])
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
    def is_on_me(self, pos):
        return self.rect[0] <= pos[0] <= self.rect[0] + self.rect[2] and self.rect[1] <= pos[1] <= self.rect[1] + self.rect[3]
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

def string_mod(string):
    answ = string
    while len(answ) > 1 and answ[0] == '0':
        answ = answ[1:]
    if answ == '':
        return '0'
    elif answ[0] == '.':
        answ = '0' + answ
    if answ[-1] == '-':
        answ = '0'
    while answ.count('.') > 1:
        answ = answ[:answ.rfind('.')] + answ[answ.rfind('.') + 1:]
    return answ

class number_cell(UI):
    value = '0'
    is_active = False
    color = [100, 100, 100]
    binding = 'None'
    units = ''
    name = ''
    multip = 1
    def __init__(self, rect=[0, 0, 100, 100], binding='None', units='', name='', color=[100, 100, 100], multipler=1):
        self.value = ''
        self.is_active = False
        self.color = color
        self.binding = binding
        self.rect = rect.copy()
        self.units = units
        self.name = name
        self.multip = multipler
    def press(self):
        global active_string
        self.is_active = True
        if active_string != None:
            return 0
        active_string = UIs.index(self)
    def release(self):
        global active_string
        self.is_active = False
        if active_string == UIs.index(self):
            active_string = None
    def on_mouse(self, action):
        global UIs
        mps = pygame.mouse.get_pos()
        res = False
        OK = True
        for ui in UIs:
            if ui != self and ui.is_on_me(mps):
                OK = False
        if OK:
            if self.rect[0] <= mps[0] <= self.rect[0] + self.rect[2] and self.rect[1] <= mps[1] <= self.rect[1] + self.rect[3]:
                res = True
                if action.type == pygame.MOUSEBUTTONDOWN:
                    if not self.is_active:
                        self.press()
                    else:
                        self.release()
            elif action.type == pygame.MOUSEBUTTONDOWN and self.is_active:
                self.release()
        return res
    def draw(self):
        #exec('global ' + (self.binding if self.binding != 'None' else 'time_stop'))
        global empty_var
        name_img = font.render(self.name, 1, [20, 20, 20])
        units_img = font.render(self.units, 1, [20, 20, 20])
        scr.blit(name_img, [self.rect[0] - name_img.get_rect()[2] - 10, self.rect[1]])
        scr.blit(units_img, [self.rect[0] + self.rect[2] + 10, self.rect[1]])
        mps = pygame.mouse.get_pos()
        if self.is_active:
            col = [int(x / 1.2) for x in self.color]
        else:
            if self.rect[0] <= mps[0] <= self.rect[0] + self.rect[2] and self.rect[1] <= mps[1] <= self.rect[1] + self.rect[3]:
                col = [int(x / 1.1) for x in self.color]
            else:
                col = self.color.copy()
        pygame.draw.rect(scr, [255, 255, 255], self.rect, 3)
        pygame.draw.rect(scr, col, self.rect)
        if self.binding != 'None':
            if self.is_active:
                self.value = string_mod(self.value)
                exec(self.binding + ' = ' + str(float(self.value) / self.multip))
            else:
                try:
                    val = str(eval(self.binding) * self.multip)
                    if '.' in val:
                        self.value = val[:min(len(val), val.find('.') + 3)]
                    else:
                        self.value = val
                except KeyError:
                    self.value = '-'
        blit_centred(scr, font.render(self.value, 1, [0, 0, 0]), vert([self.rect[0] + self.rect[2] // 2, self.rect[1] + self.rect[3] // 2]))
    def is_on_me(self, pos):
        return False#self.rect[0] <= pos[0] <= self.rect[0] + self.rect[2] and self.rect[1] <= pos[1] <= self.rect[1] + self.rect[3]

class shield(UI):
    color = [0, 0, 0]
    def __init__(self, rect=[0, 0, 0, 0], color=[0, 0, 0]):
        self.color = color.copy()
        self.rect = rect.copy()
    def on_mouse(self, action):
        _=0
    def is_on_me(self, pos):
        return False
    def draw(self):
        pygame.draw.rect(scr, [255, 255, 255], self.rect, 3)
        pygame.draw.rect(scr, self.color, self.rect)

class graph:
    values = []
    times = []
    val_bounds = [0, 0]
    time_bounds = [0, 0]
    def __init__(self, vals, times):
        keys = sorted(list(zip(times, vals)))
        

def nearest_ball(P):
    minn = 9999999999
    index = 0
    for i in objects.keys():
        obj = objects[i]
        D = obj.dist(P)
        if type(obj) == ball and D < minn:
            index = i
            minn = D
    return [index, minn]

def nearest_spring(P):
    minn = 9999999999
    index = 0
    for i in objects.keys():
        obj = objects[i]
        D = obj.dist(P)
        if type(obj) == spring and D < minn:
            index = i
            minn = D
    return [index, minn]

def nearest_object(P):
    minn = 9999999999
    index = 0
    for i in objects.keys():
        obj = objects[i]
        D = obj.dist(P)
        if D < minn:
            index = i
            minn = D
    return [index, minn]

def remove_object(ind):
    removers = []
    for i in objects.keys():
        obj = objects[i]
        if type(obj) == spring:
            if obj.A == ind or obj.B == ind:
                removers.append(i)
    for rem in removers:
        objects.pop(rem)
    objects.pop(ind)

def add_num(num):
    _=0

empty_var = 0

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
global curent_tool, editable_object
editable_object = None
curent_tool = (curent_tool + 1) % 3
self.logo_img = imload('assets/mode' + str(curent_tool) + '.bmp')
""", logo='mode0.bmp'))
UIs.append(button(rect=[81, SZY - 40, 80, 40], color=[100, 100, 150], on_press="""
global inventory_slot
inventory_slot = (inventory_slot + 1) % 3
self.logo_img = imload('assets/inventory' + str(inventory_slot) + '.bmp')
""", logo='inventory0.bmp'))
UIs.append(shield(rect=[SZX // 2 - 450, 0, 600, 75], color=[100, 100, 100]))
UIs.append(number_cell(rect=[SZX // 2 - 50, 10, 100, 25], color=[120, 120, 120], binding='WORLD_CONSTANTS[0]', multipler=1/100, name='Ускорение свободного падения', units='м/сс'))
UIs.append(number_cell(rect=[SZX // 2 - 50, 40, 100, 25], color=[120, 120, 120], binding='WORLD_CONSTANTS[1]', multipler=1, name='Гашение скорости', units=''))

keyboard_x = SZX // 2 - 225 // 2
keyboard_y = SZY - 200
k_delta_x = 0
k_delta_y = 0
k_size_x = 75
k_size_y = 50

keyboard_text = """
global active_string, UIs
if active_string != None and len(UIs[active_string].value) < 14:
    UIs[active_string].value = UIs[active_string].value + '#'
"""
erase_text = """
global active_string, UIs
if active_string != None and len(UIs[active_string].value) > 0:
    UIs[active_string].value = UIs[active_string].value[:-1]
"""
dot_text = """
global active_string, UIs
if active_string != None and len(UIs[active_string].value) < 14:
    UIs[active_string].value = UIs[active_string].value + '.'
"""

#Here we go for KEYBOARD
for i in range(0, 3):
    for j in range(0, 3):
        rct = [keyboard_x + i * (k_delta_x + k_size_x), keyboard_y + j * (k_delta_y + k_size_y), k_size_x, k_size_y]
        val = j * 3 + i + 1
        UIs.append(button(rect=rct.copy(), color=[100, 100, 100], on_press=keyboard_text.replace('#', str(val)), logo=str(val)))
UIs.append(button(rect=[keyboard_x + 0 * (k_delta_x + k_size_x), keyboard_y + 3 * (k_delta_y + k_size_y), k_size_x, k_size_y], color=[100, 100, 100], on_press=dot_text, logo='.'))
UIs.append(button(rect=[keyboard_x + 1 * (k_delta_x + k_size_x), keyboard_y + 3 * (k_delta_y + k_size_y), k_size_x, k_size_y], color=[100, 100, 100], on_press=keyboard_text.replace('#', '0'), logo='0'))
UIs.append(button(rect=[keyboard_x + 2 * (k_delta_x + k_size_x), keyboard_y + 3 * (k_delta_y + k_size_y), k_size_x, k_size_y], color=[100, 100, 100], on_press=erase_text, logo='<'))

tm = time.monotonic()
curent_spring = None
object_counting = 0

background = pygame.Surface([SZX, SZY])
background.fill([50, 100, 50])
line_color = [75, 100, 75]
for i in range(0, SZX, 100):
    pygame.draw.line(background, line_color, [i, 0], [i, SZY])
for i in range(0, SZY, 100):
    pygame.draw.line(background, line_color, [0, i], [SZX, i])
for i in range(0, SZX, 100):
    for j in range(0, SZY, 100):
        background.blit(font_small.render(str(i // 100) + ' ' + str(j // 100), 1, [100, 100, 100]), [i + 2, j])
while kg:
    try:
        TM = time.monotonic()
        delta_time = (TM - tm) * time_stop
        tm = TM
        scr.blit(background, [0, 0])
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
                        objects[object_counting] = ball(vert(mpos), 'static')
                        object_counting += 1
                    if inventory_slot == 1:
                        objects[object_counting] = ball(vert(mpos), 'weight')
                        object_counting += 1
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
                        editable_object = nearest_object(vert(mpos))[0]
                        for ind in range(indexes_to_remove):
                            UIs.pop()
                        indexes_to_remove = 0
                        UIcolor = [120, 120, 120]
                        start_x = SZX - 400
                        step_y = 30
                        start_y = 20
                        size_x = 300
                        size_y = 25
                        if type(objects[editable_object]) == spring:
                            indexes_to_remove = 4
                            UIs.append(shield(rect=[start_x - 300, start_y - 10, 300 + SZX, 105], color=[100, 100, 100]))
                            UIs.append(number_cell(rect=[start_x, start_y + 0 * step_y, size_x, size_y], color=UIcolor, binding='objects[' + str(editable_object) + '].K', multipler = 1, name='K', units=''))
                            UIs.append(number_cell(rect=[start_x, start_y + 1 * step_y, size_x, size_y], color=UIcolor, binding='objects[' + str(editable_object) + '].X_zero', multipler = 1/100, name='Начальная длина', units='м'))
                            UIs.append(number_cell(rect=[start_x, start_y + 2 * step_y, size_x, size_y], color=UIcolor, binding='objects[' + str(editable_object) + '].TForce', multipler = 10, name='Натяжение', units='Н'))
                        elif type(objects[editable_object]) == ball:
                            indexes_to_remove = 6
                            UIs.append(shield(rect=[start_x - 300, start_y - 10, 300 + SZX, 175], color=[100, 100, 100]))
                            UIs.append(number_cell(rect=[start_x, start_y + 0 * step_y, size_x, size_y], color=UIcolor, binding='objects[' + str(editable_object) + '].pos.x', multipler = 1/100, name='Позиция по X', units='м'))
                            UIs.append(number_cell(rect=[start_x, start_y + 1 * step_y, size_x, size_y], color=UIcolor, binding='objects[' + str(editable_object) + '].pos.y', multipler = 1/100, name='Позиция по Y', units='м'))
                            UIs.append(number_cell(rect=[start_x, start_y + 2 * step_y, size_x, size_y], color=UIcolor, binding='objects[' + str(editable_object) + '].mass', multipler = 1, name='Масса', units='кг'))
                            UIs.append(number_cell(rect=[start_x, start_y + 3 * step_y, size_x, size_y], color=UIcolor, binding='objects[' + str(editable_object) + '].vel.x', multipler = 1/100, name='Скорость по X', units='м/с'))
                            UIs.append(number_cell(rect=[start_x, start_y + 4 * step_y, size_x, size_y], color=UIcolor, binding='objects[' + str(editable_object) + '].vel.y', multipler = 1/100, name='Скорость по Y', units='м/с'))
            if event.type == pygame.MOUSEBUTTONUP and (not rs):
                if curent_tool == 0:
                    if inventory_slot == 2:
                        try:
                            nb = nearest_ball(vert(mpos))[0]
                            if nb != curent_spring and nearest_spring != None:
                                objects[object_counting] = spring(curent_spring, nb, K=1000)
                                object_counting += 1
                            curent_spring = None
                        except KeyError:
                            _=0
        if curent_tool != 2:
            #print(len(UIs), indexes_to_remove)
            for ind in range(indexes_to_remove):
                UIs.pop()
            indexes_to_remove = 0
        for i in objects.keys():
            objects[i].highlight = False
            nr = nearest_object(vert(mpos))
        if editable_object != None:
            objects[editable_object].highlight = True
        if curent_spring != None:
            nb = nearest_ball(vert(mpos))[0]
            objects[nb].highlight = True
            objects[curent_spring].highlight = True
            pygame.draw.line(scr, [255, 255, 255], objects[nb].pos.get_arr(), objects[curent_spring].pos.get_arr(), 3)
        for obj in objects.values():
            if type(obj) == spring:
                obj.update()
                obj.draw(scr)
        for obj in objects.values():
            if type(obj) == ball:
                obj.update()
                obj.draw(scr)
        for U in UIs:
            U.draw()
        pygame.display.update()
    except Exception as ER:
        print(ER)
pygame.quit()
