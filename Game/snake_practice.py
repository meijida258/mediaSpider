import pygame, sys, random
import math, time
from pygame.locals import *

width = 300
length = 200
FPS = 10

pygame.init()
fpsClock = pygame.time.Clock()
screen = pygame.display.set_mode((width, length), 0, 32)

path = [{(60, 160): (60, 180), (40, 180): (60, 180)}, {(60, 140): (60, 160), (40, 160): (40, 180), (20, 180): (40, 180)}, {(60, 120): (60, 140), (0, 180): (20, 180), (20, 160): (20, 180), (40, 140): (40, 160)}, {(40, 120): (40, 140), (0, 160): (0, 180), (60, 100): (60, 120), (20, 140): (40, 140)}, {(40, 100): (60, 100), (60, 80): (60, 100), (0, 140): (20, 140), (20, 120): (20, 140)}, {(40, 80): (60, 80), (20, 100): (20, 120), (80, 80): (60, 80), (0, 120): (20, 120)}, {(0, 100): (0, 120), (20, 80): (20, 100)}, {(0, 80): (20, 80)}, {}]
snake = [(60, 180), (80, 180), (80, 160), (80, 140), (80, 120), (80, 100), (100, 100), (100, 80), (120, 80), (120, 60), (100, 60), (80, 60), (60, 60), (40, 60), (20, 60), (0, 60), (0, 40), (0, 20), (20, 20), (40, 20), (40, 0), (60, 0), (80, 0), (100, 0), (120, 0), (140, 0), (140, 20), (140, 40), (140, 60), (160, 60), (180, 60), (200, 60), (220, 60)]
def draw_reseau():# 画网格
    global screen
    color = (100,255,100)
    line_width = 1
    for i in range(1, int(length/20)):
        pygame.draw.line(screen, color, (0, i*20), (width, i*20), line_width)
    for i in range(1, int(width/20)):
        pygame.draw.line(screen, color, (i*20, 0), (i*20, length), line_width)

def draw_path(path):
    global screen
    for each_step in path:
        if each_step:
            for step in each_step.items():
                pygame.draw.rect(screen, (0,0,255),((step[0]), (20,20)))
                pygame.draw.rect(screen, (0, 0, 255), ((step[1]), (20, 20)))

def draw_snake(snake):
    global screen
    pygame.draw.rect(screen, (0,0,0),((snake[0],(20,20))))
    pygame.draw.rect(screen, (123, 11, 0), ((snake[-1], (20, 20))))
    for snake_body in snake[1:-1]:
        pygame.draw.rect(screen, (255, 0, 0), ((snake_body, (20, 20))))

while True:
    screen.fill((255, 255, 255))

    # 画网格
    draw_reseau()
    draw_path(path)
    draw_snake(snake)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    pygame.display.update()