import shlex
import socket


HOST = "127.0.0.1"
PORT = 1337
SIZE = 10


class Game:
	def __init__(self) -> None:
		self.player_x = 0
		self.player_y = 0
		self.monsters = {}  # (x, y) -> (name, hello, hp)

	def wrap_coord(self, n: int) -> int:
		return n % SIZE

	def encounter(self, x: int, y: int):
		key = (x, y)
		if key in self.monsters:
			name, hello, hp = self.monsters[key]
			return name, hello
		return None

	def move(self, dx: int, dy: int):
		self.player_x = self.wrap_coord(self.player_x + dx)
		self.player_y = self.wrap_coord(self.player_y + dy)
		encounter = self.encounter(self.player_x, self.player_y)
		return self.player_x, self.player_y, encounter

	def addmon(self, name: str, hello: str, hp: int, x: int, y: int):
		key = (x, y)
		replaced = key in self.monsters
		self.monsters[key] = (name, hello, hp)
		return replaced

	def attack(self, damage: int, target: str):
		key = (self.player_x, self.player_y)
		if key not in self.monsters or self.monsters[key][0] != target:
			return False, 0, 0

		name, hello, hp = self.monsters[key]
		damage = min(damage, hp)

		hp -= damage
		if hp == 0:
			del self.monsters[key]
			return True, damage, 0
		else:
			self.monsters[key] = (name, hello, hp)
			return True, damage, hp


game = Game()


def handle_command(line: str) -> list[str]:
	parts = shlex.split(line)
	
	match parts:
		case ["move", dx, dy]:
			x, y, encounter = game.move(int(dx), int(dy))
			response = [f"MOVE {x} {y}"]
			if encounter is None:
				response.append("NO_ENCOUNTER")
			else:
				name, hello = encounter
				response.append(shlex.join(["ENCOUNTER", name, hello]))
			return response

		case ["addmon", name, hello, hp, x, y]:
			replaced = game.addmon(name, hello, int(hp), int(x), int(y))
			return [f"ADDMON {int(replaced)}"]

		case ["attack", target, damage]:
			ok, dealt, hp_left = game.attack(int(damage), target)
			if not ok:
				return ["NOT_HERE"]
			if hp_left == 0:
				return [f"KILLED {dealt}"]
			return [f"ATTACK {dealt} {hp_left}"]

		case _:
			return ["ERROR"]


def serve() -> None:
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
		server_sock.bind((HOST, PORT))
		server_sock.listen(1)

		while True:
			conn, addr = server_sock.accept()
			with conn:
				while True:
					data = b""
					while not data.endswith(b"\n"):
						chunk = conn.recv(1)
						if not chunk:
							break
						data += chunk
					if not data:
						break

					line = data.decode().strip()
					response = handle_command(line)
					message = "\n".join(response) + "\n\n"
					conn.sendall(message.encode())


if __name__ == "__main__":
	serve()
