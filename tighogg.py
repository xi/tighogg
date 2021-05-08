import boon

LEFT = 0
RIGHT = 1
YELLOW = 10
GREEN = 11


class Player:
    def __init__(self, x, y, direction, color):
        self.x = x
        self.y = y
        self.color = color
        self.direction = LEFT
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
        for line in self._render():
            line = line.replace('w', self.weapon)
            line = (
                boon.get_cap('setaf', self.color)
                + boon.get_cap('bold')
                + line
                + boon.get_cap('sgr0')
            )
            yield line


class Game(boon.App):
    def __init__(self):
        super().__init__()
        self.player1 = Player(10, 10, RIGHT, YELLOW)
        self.player2 = Player(10, 10, LEFT, GREEN)

    def render(self, rows, cols):
        yield from self.player1.render()
        yield from self.player2.render()

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


if __name__ == '__main__':
    game = Game()
    game.run()
