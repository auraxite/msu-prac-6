import cmd
import io
import shlex
from cowsay import cowsay, list_cows, read_dot_cow


SIZE = 10
JGSBAT = read_dot_cow(io.StringIO(r"""
    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\--//|.'-._  (
     )'   .'\/o\/o\/'.   `(
      ) .' . \====/ . '. (
       )  / <<    >> \  (
        '-._/``  ``\_.-'
  jgs     __\\'--'//__
         (((""`  `"")))
"""))


class Game:
    def __init__(self) -> None:
        self.player_x = 0
        self.player_y = 0
        self.monsters = {}  # (x, y) -> (name, hello, hp)

    def wrap_coord(self, n: int) -> int:
        return n % SIZE

    def encounter(self, x: int, y: int) -> None:
        key = (x, y)
        if key in self.monsters:
            name, hello, hp = self.monsters[key]
            if name == "jgsbat":
                print(cowsay(hello, cowfile=JGSBAT))
            else:
                print(cowsay(hello, cow=name))

    def move(self, dx: int, dy: int) -> None:
        self.player_x = self.wrap_coord(self.player_x + dx)
        self.player_y = self.wrap_coord(self.player_y + dy)
        print(f"Moved to ({self.player_x}, {self.player_y})")
        self.encounter(self.player_x, self.player_y)

    def addmon(self, name: str, hello: str, hp: int, x: int, y: int) -> None:
        key = (x, y)
        replaced = key in self.monsters
        self.monsters[key] = (name, hello, hp)
        print(f"Added monster {name} to ({x}, {y}) saying {hello}")
        if replaced:
            print("Replaced the old monster")

    def attack(self) -> None:
        key = (self.player_x, self.player_y)
        if key not in self.monsters:
            print("No monster here")
            return

        name, hello, hp = self.monsters[key]
        damage = min(10, hp)

        print(f"Attacked {name},  damage {damage} hp")
        hp -= damage
        if hp == 0:
            print(f"{name} died")
            del self.monsters[key]
        else:
            self.monsters[key] = (name, hello, hp)
            print(f"{name} now has {hp}")


class Shell(cmd.Cmd):
    intro = "<<< Welcome to Python-MUD 0.1 >>>"
    prompt = "(mud) "

    def __init__(self) -> None:
        super().__init__()
        self.game = Game()

    def do_up(self, arg: str) -> None:
        if arg.strip():
            print("Invalid arguments")
            return
        self.game.move(0, -1)

    def do_down(self, arg: str) -> None:
        if arg.strip():
            print("Invalid arguments")
            return
        self.game.move(0, 1)

    def do_left(self, arg: str) -> None:
        if arg.strip():
            print("Invalid arguments")
            return
        self.game.move(-1, 0)

    def do_right(self, arg: str) -> None:
        if arg.strip():
            print("Invalid arguments")
            return
        self.game.move(1, 0)

    def do_addmon(self, arg: str) -> None:
        if not arg.strip():
            print("Invalid arguments")
            return

        try:
            parts = shlex.split(arg)
        except ValueError:
            print("Invalid arguments")
            return

        name = parts[0]
        if (name not in list_cows()) and (name != "jgsbat"):
            print("Cannot add unknown monster")
            return

        params = {}
        i = 1

        try:
            while i < len(parts):
                if parts[i] == "hello":
                    if ("hello" in params) or (i + 1 >= len(parts)):
                        raise ValueError
                    params["hello"] = parts[i + 1]
                    i += 2

                elif parts[i] == "hp":
                    if ("hp" in params) or (i + 1 >= len(parts)):
                        raise ValueError
                    params["hp"] = int(parts[i + 1])
                    i += 2

                elif parts[i] == "coords":
                    if ("coords" in params) or (i + 2 >= len(parts)):
                        raise ValueError
                    params["coords"] = True
                    params["x"] = int(parts[i + 1])
                    params["y"] = int(parts[i + 2])
                    i += 3

                else:
                    raise ValueError

            if not all(k in params for k in ("hello", "hp", "coords", "x", "y")):
                raise ValueError

            hello = params["hello"]
            hp = params["hp"]
            x = params["x"]
            y = params["y"]

            if not (0 <= x < SIZE and 0 <= y < SIZE):
                raise ValueError
            if hp <= 0:
                raise ValueError

        except ValueError:
            print("Invalid arguments")
            return

        self.game.addmon(name, hello, hp, x, y)

    def do_attack(self, arg: str) -> None:
        if arg.strip():
            print("Invalid arguments")
            return
        self.game.attack()

    def do_quit(self, arg: str) -> bool:
        if arg.strip():
            print("Invalid arguments")
            return False
        return True


def main() -> None:
    Shell().cmdloop()


if __name__ == "__main__":
    main()