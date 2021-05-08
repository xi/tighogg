import sys
import shutil
import time

import boon

LEFT = 0
RIGHT = 1
YELLOW = 10
GREEN = 11
LEVEL_WIDTH = 500


class Player:
    def __init__(self, x, y, direction, color):
        self.x = x
        self.y = y
        self.base_direction = direction
        self.direction = direction
        self.color = color
        self.running = False
        self.cycle_duration = 3
        self.cycle_frame = 0
        self.cooldown = -1
        self.weapon = '-'

    def step(self):
        if self.running:
            if self.direction == RIGHT:
                self.x += 1
            else:
                self.x -= 1
        self.cooldown -= 1
        self.cycle_frame = (self.cycle_frame + 1) % (self.cycle_duration * 4)

    def die(self):
        self.cooldown = 30
        self.direction = self.base_direction
        self.running = False

    def _render(self):
        if self.running:
            if self.cycle_frame // self.cycle_duration == 0:
                yield r'    O /'
                yield r'   /\/ '
                yield r' _/\   '
                yield r'    \  '
            elif self.cycle_frame // self.cycle_duration == 1:
                yield r'    O /'
                yield r'   /\/ '
                yield r'  _\   '
                yield r'   |   '
            elif self.cycle_frame // self.cycle_duration == 2:
                yield r'    O /'
                yield r'   /\/ '
                yield r'   \   '
                yield r"  /'   "
            elif self.cycle_frame // self.cycle_duration == 3:
                yield r'    O /'
                yield r'   /\/ '
                yield r'  /\   '
                yield r" /  '  "
        else:
            yield r' \_O  /'
            yield r'   |\/ '
            yield r'   |\  '
            yield r'  / |  '

    def render(self, camera):
        for i, line in enumerate(self._render()):
            if self.direction == LEFT:
                line = line[::-1].replace('/', '1').replace('\\', '/').replace('1', '\\')
            x = round(self.x - camera) - 1 + len(line) - len(line.lstrip())
            y = self.y - 2 + i
            if x < 0:
                continue
            boon.move(y, x)
            sys.stdout.write(
                boon.get_cap('setaf', self.color)
                + boon.get_cap('bold')
                + line.strip().replace('w', self.weapon)
                + boon.get_cap('sgr0')
            )


class Game:
    def __init__(self):
        self.player1 = Player(LEVEL_WIDTH // 2 - 10, 10, RIGHT, YELLOW)
        self.player2 = Player(LEVEL_WIDTH // 2 + 10, 10, LEFT, GREEN)
        self.players = [self.player1, self.player2]
        self.running = True

    @property
    def leader(self):
        return self.players[-1]

    @property
    def straggler(self):
        return self.players[0]

    @property
    def position(self):
        return self.leader.x / LEVEL_WIDTH

    @property
    def direction(self):
        return self.leader.base_direction

    def render_hud(self):
        x = round(self.position * self.cols)
        if self.direction == RIGHT:
            bar = '=' * x + '>' + ' ' * (self.cols - x - 1)
        else:
            bar = ' ' * x + '<' + '=' * (self.cols - x - 1)
        boon.move(0, 0)
        sys.stdout.write(
            boon.get_cap('setaf', self.leader.color)
            + bar
            + boon.get_cap('sgr0')
        )

    def render(self):
        self.cols, self.rows = shutil.get_terminal_size()
        sys.stdout.write(boon.get_cap('clear'))

        if self.straggler.cooldown > 1:
            camera = self.leader.x - self.cols / 2
        else:
            camera = (self.leader.x + self.straggler.x) / 2 - self.cols / 2

        self.render_hud()

        for player in self.players:
            if player.cooldown < 0:
                player.render(camera)

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
            self.render()
            while self.running:
                last = time.time()
                self.on_key(boon.getch())

                for player in self.players:
                    player.step()
                    player.cooldown -= 1

                # die on out-of-screen
                if (
                    self.straggler.cooldown < 0
                    and abs(self.straggler.x - self.leader.x) > self.cols
                ):
                    self.straggler.die()

                # respawn on edge of screen
                if self.straggler.cooldown == 0:
                    if self.direction == RIGHT:
                        self.straggler.x = self.leader.x + self.cols / 2
                    else:
                        self.straggler.x = self.leader.x - self.cols / 2

                self.render()
                time.sleep(1 / 30 - (time.time() - last))


if __name__ == '__main__':
    game = Game()
    game.run()
