import pygame as pyg
import math
import random
import time
from numba import njit


def get_dist(p1, p2):
    return hypo(p1[0]-p2[0], p1[1]-p2[1])


@njit(fastmath=True)
def hypo(l1, l2):
    return math.sqrt((l1)**2 + (l2)**2)


class Bird():
    def __init__(self, pos=[0, 0], vlc=[0, 0], nose_color=(0, 0, 255)):
        self.pos = pos
        self.vlc = vlc
        self.cruis_vlc = 8  # pixels per second
        self.nose_color = nose_color

    def frame(self, birds, this_ind, distanses, delta_t, w, h):
        forse_out = 0.5  # forse that repels
        forse_in = 0.2
        back_forse_range = 30
        to_forse_range = 40

        new_birds = []
        for i in range(len(distanses)):
            if i != this_ind:
                new_birds.append([birds[i].pos, distanses[i][this_ind]])
        birds = new_birds

        birds = sorted(birds, key=lambda bird_tuple: bird_tuple[1])
        bird_close = birds[0]

        if bird_close[1] > w-self.pos[0]:  # neural web pro
            bird_close = [[w, self.pos[1]], w-self.pos[0]]
        if bird_close[1] > self.pos[0]:
            bird_close = [[0, self.pos[1]], self.pos[0]]
        if bird_close[1] > h-self.pos[1]:
            bird_close = [[self.pos[0], h], h-self.pos[1]]
        if bird_close[1] > self.pos[1]:
            bird_close = [[self.pos[0], 0], self.pos[1]]

        d = bird_close[1] + 0.0000001  # != 0
        if d < back_forse_range:
            self.vlc = [
                self.vlc[i] - forse_out*(bird_close[0][i] -
                                         self.pos[i])/d for i in [0, 1]]
        birds = [bird for bird in birds if bird[1] > to_forse_range]
        bird_far = birds[0]
        d = bird_far[1] + 0.0000001  # != 0
        if d > to_forse_range:
            self.vlc = [
                self.vlc[i] + forse_in*(bird_far[0][i] -
                                        self.pos[i])/d for i in [0, 1]]

        n = 1  # 1/speed stabilisator strengh
        vlc_module = hypo(*self.vlc) + 0.0000001  # != 0
        cruis_hff = self.cruis_vlc/vlc_module
        new_kff = 1 + (cruis_hff - 1)*(n*delta_t)
        self.vlc = [vlc*new_kff for vlc in self.vlc]

        self.pos = [self.pos[i] +
                    self.vlc[i]*delta_t for i in [0, 1]]

    def rend(self, window):
        pyg.draw.circle(window, (255, 255, 255), self.pos, 1)
        pyg.draw.line(window, self.nose_color, self.pos, (
            self.pos[0] + self.vlc[0],
            self.pos[1] + self.vlc[1]), 1)


pyg.init()
w, h = 800, 800

window = pyg.display.set_mode((w, h))
running = True

birds = []
for i in range(100):
    birds.append(Bird(
        [random.randint(0, w), random.randint(0, h)],
        nose_color=[random.randint(128, 255) for _ in range(3)]))


def prosess_birds(birds, delta_t):  # phisics cycle
    ammout = len(birds)
    distanses = [[0 for _ in range(ammout)] for _ in range(ammout)]
    for a in range(ammout):
        for b in range(a, ammout):
            dist = get_dist(birds[a].pos, birds[b].pos)
            distanses[b][a] = dist
            distanses[a][b] = dist

    for i in range(ammout):
        birds[i].frame(birds, i, distanses, delta_t, w, h)


t = time.time()
while running:
    # print(get_angle([10, 0], [0, 0], pyg.mouse.get_pos()))
    # print(pyg.mouse.get_pos())

    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            running = False
        if event.type == pyg.KEYDOWN:
            if event.key == pyg.K_ESCAPE:
                running = False

    window.fill((0, 0, 0))
    # s = pyg.Surface((w, h), pyg.SRCALPHA)
    # s.fill((0, 0, 0, 32))
    # window.blit(s, (0, 0))

    delta_t = 0.1  # time.time()-t
    prosess_birds(birds, delta_t)
    [bird.rend(window) for bird in birds]

    pyg.display.flip()
    # t = time.time()

pyg.quit()
