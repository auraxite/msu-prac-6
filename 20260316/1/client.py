import cmd
import io
import shlex
import socket
from cowsay import cowsay, read_dot_cow


HOST = "127.0.0.1"
PORT = 1337

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


class Shell(cmd.Cmd):
    intro = "<<< Welcome to Python-MUD 0.1 >>>"
    prompt = "(mud) "

    def __init__(self) -> None:
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

    def request(self, command: str) -> list[str]:
        self.sock.sendall((command + "\n").encode())

        response = []
        while True:
            data = b""
            while not data.endswith(b"\n"):
                chunk = self.sock.recv(1)
                if not chunk:
                    return response
                data += chunk

            line = data.decode().strip()
            if line == "":
                break
            response.append(line)

        return response

    def encounter(self, name: str, hello: str) -> None:
        if name == "jgsbat":
            print(cowsay(hello, cowfile=JGSBAT))
        else:
            print(cowsay(hello, cow=name))

    def move(self, dx: int, dy: int) -> None:
        response = self.request(shlex.join(["move", str(dx), str(dy)]))

        move_parts = shlex.split(response[0])
        x = int(move_parts[1])
        y = int(move_parts[2])
        print(f"Moved to ({x}, {y})")

        encounter_parts = shlex.split(response[1])
        if encounter_parts[0] == "ENCOUNTER":
            name = encounter_parts[1]
            hello = encounter_parts[2]
            self.encounter(name, hello)

    def do_up(self, arg: str) -> None:
        if arg.strip():
            print("Invalid arguments")
            return
        self.move(0, -1)

    def do_down(self, arg: str) -> None:
        if arg.strip():
            print("Invalid arguments")
            return
        self.move(0, 1)

    def do_left(self, arg: str) -> None:
        if arg.strip():
            print("Invalid arguments")
            return
        self.move(-1, 0)

    def do_right(self, arg: str) -> None:
        if arg.strip():
            print("Invalid arguments")
            return
        self.move(1, 0)

    def do_quit(self, arg: str) -> bool:
        if arg.strip():
            print("Invalid arguments")
            return False
        self.sock.close()
        return True


def main() -> None:
    Shell().cmdloop()


if __name__ == "__main__":
    main()