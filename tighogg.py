import boon


class Game(boon.App):
    def render(self, rows, cols):
        yield 'Hello World'

    def on_key(self, key):
        if key == 'q':
            self.running = False


if __name__ == '__main__':
    game = Game()
    game.run()
