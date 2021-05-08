import sys
import shutil
import time

import boon

LEFT = 0
RIGHT = 1
YELLOW = 10
GREEN = 11


class Player:
    def __init__(self, x, y, direction, color):
        self.x = x
        self.y = y
        self.direction = direction
        self.color = color
        self.running = False
        self.weapon = '-'

    def _render(self):
        if self.running:
            if self.direction == LEFT:
                yield r'o  '
                yield r'w\ '
            else:
                yield r'  o'
                yield r' /w'
            yield r' @ '
        else:
            yield r' o '
            if self.direction == LEFT:
                yield r'w| '
            else:
                yield r' |w'
            yield r' Λ '

    def render(self):
        for i, line in enumerate(self._render()):
            x = self.x - 1 + len(line) - len(line.lstrip())
            y = self.y - 2 + i
            boon.move(y, x)
            sys.stdout.write(
                boon.get_cap('setaf', self.color)
                + boon.get_cap('bold')
                + line.strip().replace('w', self.weapon)
                + boon.get_cap('sgr0')
            )


class Game:
    def __init__(self):
        self.player1 = Player(10, 10, RIGHT, YELLOW)
        self.player2 = Player(20, 10, LEFT, GREEN)
        self.running = True

    def render(self):
        cols, rows = shutil.get_terminal_size()
        sys.stdout.write(boon.get_cap('clear'))
        self.player1.render()
        self.player2.render()
        sys.stdout.flush()

    def on_key(self, key):
        if key == 'q':
            self.running = False

        # player1
        elif key == boon.KEY_LEFT:
            self.player1.running = True
            self.player1.direction = LEFT
        elif key == boon.KEY_RIGHT:
            self.player1.running = True
            self.player1.direction = RIGHT
        elif key == boon.KEY_DOWN:
            self.player1.running = False

        # player2
        elif key == 'a':
            self.player2.running = True
            self.player2.direction = LEFT
        elif key == 'd':
            self.player2.running = True
            self.player2.direction = RIGHT
        elif key == 's':
            self.player2.running = False

    def run(self):
        self.running = True
        with boon.fullscreen():
            while self.running:
                last = time.time()
                self.on_key(boon.getch())
                self.render()
                time.sleep(1 / 30 - (time.time() - last))


if __name__ == '__main__':
    game = Game()
    game.run()
