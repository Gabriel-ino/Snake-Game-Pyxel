import pyxel
from enum import Enum
from time import time
from random import randrange, randint
from collections import deque
from os import execl
import sys
from time import sleep
from save_data import auto_save

WIDTH = 160
HEIGHT = 120

# Snake direction labels


class Direction(Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3


class Level:
    def __init__(self):
        self.tm = 0
        self.u = 0
        self.v = 0
        self.w = 24
        self.h = 16

    def draw(self):
        pyxel.bltm(0, 0, self.tm, self.u, self.v, self.w, self.h)


class GameState(Enum):
    RUNNING = 0
    GAME_OVER = 1


"""

The Apple class creates our apple object and move it,
checking the collision too

"""


class Apple:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8

    def draw(self, x=0):
        pyxel.blt(self.x, self.y, 0, x, 0, self.w, self.h)

    def intersect(self, u, v, w, h) -> bool:
        is_intersect = False
        if u + w > self.x and self.x + self.w > u and v + h > self.y and self.y + self.h > v:
            is_intersect = True

        return is_intersect

    def move(self, new_x, new_y):
        self.x = new_x
        self.y = new_y


class SnakeSection:

    def __init__(self, x, y, is_head: bool = False):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8
        self.is_head = is_head

    def draw(self, direction):
        width = self.w
        height = self.h
        sprite_x = 8
        sprite_y = 0
        # Depending on the section, if it's the head, we need to change the sprite
        if self.is_head:
            if direction == Direction.RIGHT:
                sprite_x = 0
                sprite_y = 8
            elif direction == Direction.LEFT:
                sprite_x = 0
                sprite_y = 8
                width = width * -1
            elif direction == Direction.DOWN:
                sprite_x = 8
                sprite_y = 8
            elif direction == Direction.UP:
                sprite_x = 8
                sprite_y = 8
                height = height * -1
        pyxel.blt(self.x, self.y, 0, sprite_x, sprite_y, width, height)

    def snake_intersect(self, u, v, w, h):
        is_intersect = False
        conditions = [u + w > self.x, self.x + self.w > u, v + h > self.y, self.y + self.h > v ]
        if all(conditions):
            is_intersect = True
        return is_intersect


class Hud:
    def __init__(self):
        self.title = 'Snake Game'
        self.title_text_x = self.center_text(self.title, 196)
        self.score = str(0)
        self.score_text_x = self.right_text(self.score, 196)
        self.level = f'Level{str(0)}'
        self.level_text_x = 10

    # Calculate centered text

    @staticmethod
    def center_text(text, page_width, char_width=pyxel.FONT_WIDTH) -> int:
        text_width = len(text) * char_width
        return (page_width - text_width)/2

    # Calculate right text

    @staticmethod
    def right_text(text, page_width, char_width=pyxel.FONT_WIDTH) -> int:
        text_width = len(text) + char_width
        return page_width - (text_width + char_width)

    def draw_title(self):
        pyxel.rect(self.title_text_x - 18, 0, len(self.title) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.title_text_x - 18, 1, self.title, 12)

    def draw_score(self, score):
        self.score = str(score)

        self.score_text_x = self.right_text(self.score, 196)
        pyxel.rect(self.score_text_x - 20, 0, len(self.score) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.score_text_x - 40, 1, self.score, 3)

    def draw_level(self, level):
        self.level = f'Level {level}'
        pyxel.rect(self.level_text_x - 1, 0, len(self.level) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.level_text_x, 1, self.level, 3)


class App:

    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, scale=0, caption="Snake Game", fps=120)
        pyxel.load('assets/[pyxel_resource_file].pyxres')
        self.current_game_state = GameState.RUNNING
        self.level = Level()
        self.num_level = 1
        self.hud = Hud()
        self.apple = Apple(32, 64)
        self.snake = [SnakeSection(x, 32, is_head=True) if x == 32 else SnakeSection(x, 32) for x in range(32, 15, -8)]
        self.snake_direction = Direction.RIGHT
        self.add_section = 0
        self.speed = 3
        self.time_last_frame = time()
        self.dt = 0
        self.score = 0
        self.input_queue = deque()
        self.play_music = False
        self.time_last_move = 0
        self.x = 0
        pyxel.run(self.update, self.draw)
        if self.play_music:
            pyxel.playm(0, loop=True)

    def update(self):
        time_frame = time()
        self.dt = time_frame - self.time_last_frame
        self.time_last_frame = time_frame
        self.time_last_move += self.dt
        self.check_input()
        if self.current_game_state == GameState.GAME_OVER:
            self.start_new_game()
        if self.time_last_move >= 1 / self.speed:
            self.time_last_move = 0
            self.check_collision()
            self.move_snake()

        if self.num_level == 1:
            if self.score % 10 == 0 and self.score != 0:
                self.num_level += 1
                self.reset_snake()
                sleep(0.3)
        else:
            if self.score % 10 == 0 and self.score / self.num_level == 10:
                self.num_level += 1
                self.reset_snake()
                sleep(0.3)

    def toggle_sound(self):
        if self.play_music:
            self.play_music = False
            pyxel.stop()
        else:
            self.play_music = True
            pyxel.playm(0, loop=True)

    def reset_snake(self):
        self.snake = [SnakeSection(x, 32, is_head=True) if x == 32 else SnakeSection(x, 32) for x in range(32, 15, -8)]
        self.speed = 3

    def start_new_game(self):
        auto_save()
        sleep(3)
        execl(sys.executable, sys.executable, *sys.argv)  # This function will reinitialize the program
        if self.play_music:
            pyxel.playm(0, loop=True)

    def draw(self):
        pyxel.cls(0)
        self.level.draw()
        self.apple.draw()
        for s in self.snake:
            s.draw(self.snake_direction)
        self.hud.draw_title()
        self.hud.draw_score(self.score)
        self.hud.draw_level(self.num_level)

        if self.current_game_state == GameState.GAME_OVER:
            pyxel.text(80, 60, 'GAME OVER', 8)

    def check_collision(self):
        # Apple
        if self.apple.intersect(self.snake[0].x, self.snake[0].y, self.snake[0].w, self.snake[0].h):
            pyxel.play(3, 0)
            self.score += 1
            self.speed += (self.speed * 0.1)
            self.add_section += 4
            self.move_apple()

        # Snake's Tail

        for s in self.snake:
            if s == self.snake[0]:
                continue
            if s.snake_intersect(self.snake[0].x, self.snake[0].y, self.snake[0].w, self.snake[0].h):
                pyxel.stop()
                pyxel.play(0, 1)
                self.current_game_state = GameState.GAME_OVER

        if pyxel.tilemap(0).get(self.snake[0].x/8, self.snake[0].y/8) == 3:
            pyxel.stop()
            pyxel.play(0, 1)
            self.current_game_state = GameState.GAME_OVER

    def move_apple(self):
        good_position = False
        while not good_position:
            new_x = randrange(8, WIDTH-8, 8)
            new_y = randrange(8, HEIGHT-8, 8)
            good_position = True

            for s in self.snake:
                if (
                        new_x + 8 > s.x and
                        s.x + s.w > new_x and
                        new_y + 8 > s.y and
                        s.y + s.h > new_y
                ):
                    good_position = False
                    break

                # Check Wall

                if good_position:
                    self.apple.move(new_x, new_y)

    def move_snake(self):
        if len(self.input_queue):
            self.snake_direction = self.input_queue.popleft()
        # Grow snake
        if self.add_section > 0:
            self.snake.append(SnakeSection(self.snake[-1].x, self.snake[-1].y))
            self.add_section -= 1
        # Moving Head:
        previous_location_x = self.snake[0].x
        previous_location_y = self.snake[0].y

        if self.snake_direction == Direction.RIGHT:
            self.snake[0].x += self.snake[0].w
        if self.snake_direction == Direction.LEFT:
            self.snake[0].x -= self.snake[0].w
        if self.snake_direction == Direction.UP:
            self.snake[0].y -= self.snake[0].w
        if self.snake_direction == Direction.DOWN:
            self.snake[0].y += self.snake[0].w

        # Moving Tail:
        for s in self.snake:
            if s == self.snake[0]:
                continue
            current_location_x = s.x
            current_location_y = s.y
            s.x = previous_location_x
            s.y = previous_location_y
            previous_location_x = current_location_x
            previous_location_y = current_location_y

    def check_input(self):
        buttons = [pyxel.KEY_RIGHT, pyxel.KEY_LEFT, pyxel.KEY_DOWN, pyxel.KEY_UP]
        direction = [Direction.RIGHT, Direction.LEFT, Direction.DOWN, Direction.UP]
        if pyxel.btnp(pyxel.KEY_M):
            self.toggle_sound()
        for button in range(len(buttons)):
            if pyxel.btn(buttons[button]):
                if len(self.input_queue) == 0:
                    if button % 2 == 0 or button == 0:
                        if self.snake_direction != direction[button + 1] and self.snake_direction != direction[button]:
                            self.input_queue.append(direction[button])
                    else:
                        if self.snake_direction != direction[button - 1] and self.snake_direction != direction[button]:
                            self.input_queue.append(direction[button])

                else:
                    if button % 2 == 0 or button == 0:
                        if self.input_queue[-1] != direction[button + 1] and self.input_queue[-1] != direction[button]:
                            self.input_queue.append(direction[button])

                    else:
                        if self.input_queue[-1] != direction[button - 1] and self.input_queue[-1] != direction[button]:
                            self.input_queue.append(direction[button])


if __name__ == '__main__':
    App()def snake_intersect(self, u, v, w, h):
        is_intersect = False
        conditions = [u + w > self.x, self.x + self.w > u, v + h > self.y, self.y + self.h > v ]
        if all(conditions):
            is_intersect = True
        return is_intersect
