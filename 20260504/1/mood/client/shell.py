import cmd
import cowsay
import io
import pathlib
import readline
import shlex
import socket
import threading
import time
import webbrowser

from mood.common.const import HOST, PORT, SIZE


with pathlib.Path(__file__).with_name("custom_monsters").joinpath("jgsbat.txt").open(encoding="utf-8") as cowfile:
	JGSBAT = cowsay.read_dot_cow(cowfile)

DOCS = pathlib.Path(__file__).resolve().parents[2] / "docs" / "build" / "html" / "index.html"


class Shell(cmd.Cmd):
	intro = "<<< Welcome to Python-MUD 0.1 >>>"
	prompt = "(mud) "

	def __init__(self, username) -> None:
		super().__init__()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((HOST, PORT))
		self.weapons = {
			"sword": 10,
			"spear": 15,
			"axe": 20,
		}
		self.alive = True
		self.sock.sendall(shlex.join(["login", username]).encode() + b"\n")
		threading.Thread(target=self.reader_loop, daemon=True).start()

	def encounter(self, name: str, hello: str) -> str:
		if name == "jgsbat":
			return cowsay.cowsay(hello, cowfile=JGSBAT)
		return cowsay.cowsay(hello, cow=name)

	def format_message(self, line: str) -> str:
		try:
			parts = shlex.split(line)
		except ValueError:
			return line

		if len(parts) == 3 and parts[0] == "ENCOUNTER":
			return self.encounter(parts[1], parts[2])

		return line

	def reader_loop(self) -> None:
		while self.alive:
			try:
				data = b""
				while not data.endswith(b"\n"):
					chunk = self.sock.recv(1)
					if not chunk:
						self.alive = False
						print("\nDisconnected from server")
						return
					data += chunk

				line = data.decode().strip()
				if line == "":
					continue
				line = self.format_message(line)
				current = readline.get_line_buffer()
				print("\r" + line)
				print(f"{self.prompt}{current}", end="", flush=True)

			except:
				self.alive = False
				return

	def send_command(self, command: str) -> None:
		if not self.alive:
			return
		self.sock.sendall((command + "\n").encode())

	def run_file(self, filename: str) -> None:
		with open(filename, encoding="utf-8") as mood_file:
			for line in mood_file:
				command = line.strip()
				if not command:
					continue
				if command == "quit":
					self.do_quit("")
					return
				self.send_command(command)
				time.sleep(1)

	def move(self, dx: int, dy: int) -> None:
		self.send_command(shlex.join(["move", str(dx), str(dy)]))

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
		if (name not in cowsay.list_cows()) and (name != "jgsbat"):
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

		self.send_command(
			shlex.join(["addmon", name, hello, str(hp), str(x), str(y)])
		)

	def do_attack(self, arg: str) -> None:
		if not arg.strip():
			print("Invalid arguments")
			return

		try:
			parts = shlex.split(arg)
		except ValueError:
			print("Invalid arguments")
			return

		target = parts[0]
		weapon = "sword"

		if len(parts) == 1:
			pass
		elif len(parts) == 3 and parts[1] == "with":
			weapon = parts[2]
		else:
			print("Invalid arguments")
			return

		if weapon not in self.weapons:
			print("Unknown weapon")
			return

		damage = self.weapons[weapon]
		self.send_command(shlex.join(["attack", target, weapon, str(damage)]))

	def complete_attack(self, text: str, line: str, begidx: int, endidx: int) -> list[str]:
		try:
			parts = shlex.split(line[:begidx])
		except ValueError:
			return []

		monsters = cowsay.list_cows() + ["jgsbat"]

		if len(parts) == 1:
			options = monsters
		elif len(parts) == 2:
			options = ["with"]
		elif len(parts) == 3 and parts[2] == "with":
			options = list(self.weapons.keys())
		else:
			return []

		return [x for x in options if x.startswith(text)]

	def do_quit(self, arg: str) -> bool:
		if arg.strip():
			print("Invalid arguments")
			return False
		self.alive = False
		self.sock.close()
		return True

	do_EOF = do_quit

	def do_sayall(self, arg: str) -> None:
		if not arg.strip():
			print("Invalid arguments")
			return
		self.send_command(shlex.join(["sayall", arg]))

	def do_movemonsters(self, arg: str) -> None:
		mode = arg.strip()
		if mode not in {"on", "off"}:
			print("Invalid arguments")
			return
		self.send_command(shlex.join(["movemonsters", mode]))

	def do_locale(self, arg: str) -> None:
		try:
			(locale_name,) = shlex.split(arg)
		except ValueError:
			print("Invalid arguments")
			return
		self.send_command(shlex.join(["locale", locale_name]))

	def do_documentation(self, arg: str) -> None:
		if arg.strip():
			print("Invalid arguments")
			return

		if not DOCS.exists():
			print("Documentation is not built")
			return

		webbrowser.open(DOCS.as_uri())
