import sys
import shutil
import time
import math

import boon

LEFT = 0
RIGHT = 1
YELLOW = 10
GREEN = 11

BLOCK_HEIGHT = 5
BLOCK_WIDTH = 15
RUN_VELOCITY = 1
GRAVITY = 0.1

# x(t) = t * RUN_VELOCITY
# y(t) = t**2 * GRAVITY / 2 - t * JUMP_VELOCITY
# A single jump should cover BLOCK_WIDTH and BLOCK_HEIGHT
JUMP_VELOCITY = ((BLOCK_WIDTH / RUN_VELOCITY) ** 2 * GRAVITY / 2 + BLOCK_HEIGHT) / (BLOCK_WIDTH / RUN_VELOCITY)  # noqa


class Map:
    def __init__(self, s='------__ _ _-- ____---- --'):
        self.s = s

    @property
    def size(self):
        return len(self.s) * BLOCK_WIDTH * 2

    def get_floor(self, x):
        k = abs(round(x / BLOCK_WIDTH) - len(self.s))
        try:
            if self.s[k] == '-':
                return 0
            elif self.s[k] == '_':
                return BLOCK_HEIGHT
        except IndexError:
            pass
        return math.inf

    def render(self, camera, cols, rows):
        sys.stdout.write(boon.get_cap('setaf', 7))
        for x in range(cols):
            y = self.get_floor(camera + x)
            if y is math.inf:
                continue
            boon.move(y + rows // 2 + 1, x)
            sys.stdout.write('#')
        sys.stdout.write(boon.get_cap('sgr0'))


class Player:
    def __init__(self, game, x, y, direction, color):
        self.game = game
        self.x = x
        self.y = y
        self.dy = 0
        self.base_direction = direction
        self.direction = direction
        self.color = color
        self.running = False
        self.cycle_duration = 3
        self.cycle_frame = 0
        self.cooldown = -1
        self.alive = True

    @property
    def floor(self):
        return min(
            self.game.map.get_floor(self.x - 2),
            self.game.map.get_floor(self.x + 2),
        )

    def step(self):
        if self.running:
            old_x = self.x
            if self.direction == RIGHT:
                self.x += RUN_VELOCITY
            else:
                self.x -= RUN_VELOCITY
            if self.floor < self.y:
                self.x = old_x
                self.running = False

        if self.floor > self.y:
            self.dy += GRAVITY
        self.y += self.dy
        if self.floor < self.y:
            self.dy = 0
            self.y = self.floor

        self.cooldown -= 1
        self.cycle_frame = (self.cycle_frame + 1) % (self.cycle_duration * 4)

    def die(self):
        if not self.alive:
            return
        self.alive = False
        self.cooldown = 30
        self.direction = self.base_direction
        self.running = False

        if self == self.game.leader:
            a = self.game.players.pop(0)
            self.game.players.append(a)

    def jump(self):
        if self.floor == self.y:
            self.dy = -JUMP_VELOCITY

    def _render(self):
        if self.dy > 0:
            yield r' __O  /'
            yield r'   /\/ '
            yield r'   \\  '
            yield r'    \\ '
        elif self.dy < 0:
            yield r'  _O  /'
            yield r' / |\/ '
            yield r' _/ \  '
            yield r'     \ '
        elif self.running:
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

    def render(self, camera, cols, rows):
        sys.stdout.write(
            boon.get_cap('setaf', self.color)
            + boon.get_cap('bold')
        )
        for i, line in enumerate(self._render()):
            if self.direction == LEFT:
                line = (
                    line[::-1]
                    .replace('/', '1')
                    .replace('\\', '/')
                    .replace('1', '\\')
                )
            x = round(self.x - camera) - 3
            y = round(self.y - 3 + i)
            for j, c in enumerate(line):
                if c != ' ':
                    boon.move(y + rows // 2, x + j)
                    sys.stdout.write(c)
        sys.stdout.write(boon.get_cap('sgr0'))


class Game:
    def __init__(self):
        self.map = Map()
        self.player1 = Player(self, self.map.size // 2 - 10, 0, RIGHT, YELLOW)
        self.player2 = Player(self, self.map.size // 2 + 10, 0, LEFT, GREEN)
        self.players = [self.player1, self.player2]
        self.running = True
        self.camera = self.map.size / 2

    @property
    def leader(self):
        return self.players[-1]

    @property
    def straggler(self):
        return self.players[0]

    @property
    def position(self):
        return self.leader.x / self.map.size

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

        if not self.straggler.alive:
            camera = self.leader.x - self.cols / 2
        else:
            camera = (self.leader.x + self.straggler.x) / 2 - self.cols / 2
        self.camera = (self.camera + camera) / 2

        self.map.render(self.camera, self.cols, self.rows)
        self.render_hud()

        for player in self.players:
            if player.alive:
                player.render(self.camera, self.cols, self.rows)

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
        elif key == boon.KEY_UP:
            self.player1.jump()

        # player2
        elif key == 'a':
            self.player2.running = True
            self.player2.direction = LEFT
        elif key == 'd':
            self.player2.running = True
            self.player2.direction = RIGHT
        elif key == 's':
            self.player2.running = False
        elif key == 'w':
            self.player2.jump()

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

                if self.direction == LEFT:
                    if self.leader.x < 0:
                        self.running = False
                else:
                    if self.leader.x > self.map.size:
                        self.running = False

                # die on out-of-screen
                distance = abs(self.straggler.x - self.leader.x)
                if distance > self.cols - 2 * BLOCK_WIDTH:
                    self.straggler.die()

                # die on abyss
                for player in self.players:
                    if player.y > 2 * BLOCK_HEIGHT:
                        player.die()

                # respawn on edge of screen
                if not self.straggler.alive and self.straggler.cooldown <= 0:
                    if self.direction == RIGHT:
                        x = self.leader.x + self.cols / 2
                    else:
                        x = self.leader.x - self.cols / 2
                    if self.map.get_floor(x) is not math.inf:
                        self.straggler.x = x
                        self.straggler.alive = True

                self.render()
                time.sleep(1 / 30 - (time.time() - last))


if __name__ == '__main__':
    game = Game()
    game.run()
