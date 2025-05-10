import pygame
import random
import time
import os

colors = [
    (93, 109, 126),
    (241, 148, 138),
    (210, 180, 222),
    (174, 214, 241),
    (171, 235, 198),
    (249, 231, 159),
    (248, 196, 113),
    (241, 120, 184),
]

class Figure:
    x = 0
    y = 0

    figures = [
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[2, 6, 3], [2, 6, 7], [3, 7, 6], [3, 7, 2]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[1, 5, 9], [4, 5, 6]],
        [[1, 2, 5, 6]],
        [[2, 6], [3, 2]],
        [[2, 2]],
    ]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(self.figures) - 1)
        self.color = random.randint(1, len(colors) - 1)
        self.rotation = 0

    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])


class Tetris:
    def __init__(self, height, width):
        self.level = 2
        self.score = 0
        self.state = "start"
        self.field = []
        self.height = height
        self.width = width
        self.x = 100
        self.y = 60
        self.zoom = 20
        self.figure = None
        self.lives = 3
        self.lost_life_message = False
        self.message_timer = 0
        self.last_blocks = []

        for i in range(height):
            self.field.append([0 for _ in range(width)])

    def new_figure(self):
        self.figure = Figure(3, 0)

    def intersects(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    x = j + self.figure.x
                    y = i + self.figure.y
                    if x < 0 or x >= self.width or y >= self.height:
                        return True
                    if self.field[y][x] > 0:
                        return True
        return False

    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            if 0 not in self.field[i]:
                lines += 1
                for j in range(self.width):
                    self.field[i][j] = 0
                for k in range(i, 1, -1):
                    self.field[k] = self.field[k - 1][:]
        self.score += lines ** 2

    def go_space(self):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    x = j + self.figure.x
                    y = i + self.figure.y
                    if 0 <= y < self.height and 0 <= x < self.width:
                        self.field[y][x] = self.figure.color
                        self.last_blocks.append((y, x))
        self.break_lines()
        self.new_figure()

        if self.intersects():
            self.lives -= 1
            if self.lives >= 1:
                for _ in range(10):
                    if self.last_blocks:
                        y, x = self.last_blocks.pop()
                        self.field[y][x] = 0
                self.new_figure()
                self.lost_life_message = True
                self.message_timer = 60
            else:
                self.state = "gameover"

    def go_side(self, dx):
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation


# Initialize pygame
pygame.init()
pygame.mixer.init()

pygame.mixer.init()
base_path = os.path.dirname(__file__)
music_path = os.path.join(base_path, "song.mp3")
pygame.mixer.music.load(music_path)
pygame.mixer.music.play(-1)


BLUE = (41, 128, 185)
LIGHT_BLUE = (231, 250, 255)
GRAY = (128, 128, 128)

size = (400, 500)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("New Tetris")

done = False
clock = pygame.time.Clock()
fps = 25
game = Tetris(20, 10)
counter = 0
pressing_down = False

start_time = time.time()
end_time = None

while not done:
    if game.figure is None:
        game.new_figure()
    counter += 1
    if counter > 100000:
        counter = 0

    if counter % (fps // game.level // 2) == 0 or pressing_down:
        if game.state == "start":
            game.go_down()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                game.rotate()
            if event.key == pygame.K_DOWN:
                pressing_down = True
            if event.key == pygame.K_LEFT:
                game.go_side(-1)
            if event.key == pygame.K_RIGHT:
                game.go_side(1)
            if event.key == pygame.K_SPACE:
                game.go_space()
            if event.key == pygame.K_ESCAPE:
                game = Tetris(20, 10)
                start_time = time.time()
                end_time = None
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                pressing_down = False

    screen.fill(LIGHT_BLUE)

    for i in range(game.height):
        for j in range(game.width):
            pygame.draw.rect(screen, GRAY, [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
            if game.field[i][j] > 0:
                pygame.draw.rect(screen, colors[game.field[i][j]],
                                 [game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 2, game.zoom - 2])

    if game.figure is not None:
        for i in range(4):
            for j in range(4):
                if i * 4 + j in game.figure.image():
                    pygame.draw.rect(screen, colors[game.figure.color],
                                     [game.x + game.zoom * (j + game.figure.x) + 1,
                                      game.y + game.zoom * (i + game.figure.y) + 1,
                                      game.zoom - 2, game.zoom - 2])


    if game.state != "gameover":
        elapsed_time = int(time.time() - start_time)
    else:
        if end_time is None:
            end_time = int(time.time() - start_time)
        elapsed_time = end_time

    font = pygame.font.SysFont('Calibri', 25, True, False)
    font1 = pygame.font.SysFont('Calibri', 55, True, False)
    text_score = font.render("Score: " + str(game.score), True, BLUE)
    text_lives = font.render("Lives: " + str(game.lives), True, BLUE)
    text_timer = font.render(f"Time: {elapsed_time} sec", True, BLUE)
    screen.blit(text_score, [0, 0])
    screen.blit(text_lives, [0, 30])
    screen.blit(text_timer, [270, 0])

    if game.lost_life_message:
        text_lost_life = font.render("    You lost a live!", True, (255, 8, 94 ))
        screen.blit(text_lost_life, [100, 160])
        game.message_timer -= 1
        if game.message_timer <= 0:
            game.lost_life_message = False

    if game.state == "gameover":
        text_game_over = font1.render("    Game Over", True, (231, 84, 187))
        text_restart = font1.render(     " Press ESC",   True, (42, 184, 234))
        text_final_time = font.render(f"   Game Time: {end_time} sec", True, (170, 0, 220))
        screen.blit(text_game_over, [20, 200])
        screen.blit(text_restart, [80, 280])
        screen.blit(text_final_time, [90, 360])

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()