import shlex
import sys
from cowsay import cowsay, list_cows, read_dot_cow


SIZE = 10


with open("cows/jgsbat.cow", encoding="utf-8") as f:
    JGSBAT = read_dot_cow(f)


class Game:
    def __init__(self) -> None:
        self.player_x = 0
        self.player_y = 0
        self.monsters = {} # (int, int) -> (str, str) name, hello

    def wrap_coord(self, n: int) -> int:
        return n % SIZE

    def encounter(self, x: int, y: int) -> None:
        key = (x, y)
        if key not in self.monsters:
            return

        name, hello = self.monsters[key]

        if name == "jgsbat":
            print(cowsay(hello, cowfile=JGSBAT))
        else:
            print(cowsay(hello, cow=name))

    def move(self, dx: int, dy: int) -> None:
        self.player_x = self.wrap_coord(self.player_x + dx)
        self.player_y = self.wrap_coord(self.player_y + dy)
        print(f"Moved to ({self.player_x}, {self.player_y})")
        self.encounter(self.player_x, self.player_y)

    def addmon(self, name: str, x: int, y: int, hello: str) -> None:
        key = (x, y)
        replaced = key in self.monsters
        self.monsters[key] = (name, hello)
        print(f"Added monster {name} to ({x}, {y}) saying {hello}")
        if replaced:
            print("Replaced the old monster")

    def process_line(self, line: str) -> None:
        line = line.strip()
        if not line:
            return

        parts = shlex.split(line)
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
            if len(parts) != 5:
                print("Invalid arguments")
                return
            try:
                name = parts[1]
                x = int(parts[2])
                y = int(parts[3])
                hello = parts[4]
            except Exception:
                print("Invalid arguments")
                return

            if not (0 <= x < SIZE and 0 <= y < SIZE):
                print("Invalid arguments")
                return
            if (name not in list_cows()) and (name != "jgsbat"):
                print("Cannot add unknown monster")
                return

            self.addmon(name, x, y, hello)
            return

        print("Invalid command")


def main() -> None:
    print("<<< Welcome to Python-MUD 0.1 >>>")
    game = Game()
    for line in sys.stdin:
        game.process_line(line)


if __name__ == "__main__":
    main()