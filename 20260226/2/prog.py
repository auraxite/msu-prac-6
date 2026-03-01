import sys
from cowsay import cowsay


SIZE = 10


class Game:
    def __init__(self) -> None:
        self.player_x = 0
        self.player_y = 0
        self.monsters = {} # (int, int) -> str

    def wrap_coord(self, n: int) -> int:
        return n % SIZE

    def encounter(self, x: int, y: int) -> None:
        key = (x, y)
        if key in self.monsters:
            hello = self.monsters[key]
            print(cowsay(hello))

    def move(self, dx: int, dy: int) -> None:
        self.player_x = self.wrap_coord(self.player_x + dx)
        self.player_y = self.wrap_coord(self.player_y + dy)
        print(f"Moved to ({self.player_x}, {self.player_y})")
        self.encounter(self.player_x, self.player_y)

    def addmon(self, x: int, y: int, hello: str) -> None:
        key = (x, y)
        replaced = key in self.monsters
        self.monsters[key] = hello
        print(f"Added monster to ({x}, {y}) saying {hello}")
        if replaced:
            print("Replaced the old monster")

    def process_line(self, line: str) -> None:
        line = line.strip()
        if not line:
            return

        parts = line.split()
        cmd = parts[0]

        if cmd in ("up", "down", "left", "right"):
            if len(parts) != 1:
                print("Invalid arguments")
                return
            if cmd == "up":
                self.move(0, -1)
            elif cmd == "down":
                self.move(0, 1)
            elif cmd == "left":
                self.move(-1, 0)
            elif cmd == "right":
                self.move(1, 0)
            return

        if cmd == "addmon":
            if len(parts) != 4:
                print("Invalid arguments")
                return
            try:
                x = int(parts[1])
                y = int(parts[2])
                hello = parts[3]
            except Exception:
                print("Invalid arguments")
                return

            if not (0 <= x < SIZE and 0 <= y < SIZE):
                print("Invalid arguments")
                return

            self.addmon(x, y, hello)
            return

        print("Invalid command")


def main() -> None:
    game = Game()
    for line in sys.stdin:
        game.process_line(line)


if __name__ == "__main__":
    main()