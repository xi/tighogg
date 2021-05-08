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
        self.ducking = False
        self.weapon = '-'

    def _render(self):
        if self.running:
            if self.ducking:
                return (
                    r'     ',
                    r'o_   ',
                    r'  @  ',
                )
            else:
                return (
                    r'o    ',
                    r'w\   ',
                    r'  @  ',
                )
                return 'o    \n \\'
        else:
            if self.ducking:
                return (
                    r'     ',
                    r'  o  ',
                    r'  Z  ',
                )
            else:
                return (
                    r'  o  ',
                    r' w|  ',
                    r'  Λ  ',
                )

    def render(self):
        for line in self._render():
            if self.direction == RIGHT:
                line = line[::-1]
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
        return self.player1.render()

    def on_key(self, key):
        if key == 'q':
            self.running = False


if __name__ == '__main__':
    game = Game()
    game.run()
