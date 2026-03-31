import asyncio
import shlex


HOST = "127.0.0.1"
PORT = 1337
SIZE = 10


class Game:
	def __init__(self) -> None:
		self.players = {} # username -> [x, y]
		self.monsters = {}  # (x, y) -> (name, hello, hp)

	def wrap_coord(self, n: int) -> int:
		return n % SIZE

	def encounter(self, x: int, y: int):
		key = (x, y)
		if key in self.monsters:
			name, hello, hp = self.monsters[key]
			return name, hello
		return None

	def move(self, username: str, dx: int, dy: int):
		x, y = self.players[username]
		x = self.wrap_coord(x + dx)
		y = self.wrap_coord(y + dy)
		self.players[username] = [x, y]
		encounter = self.encounter(x, y)
		return x, y, encounter

	def addmon(self, name: str, hello: str, hp: int, x: int, y: int):
		key = (x, y)
		replaced = key in self.monsters
		self.monsters[key] = (name, hello, hp)
		return replaced

	def attack(self, username: str, damage: int, target: str):
		x, y = self.players[username]
		key = (x, y)
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
clients = {} # username -> writer


async def broadcast(line: str):
    for w in list(clients.values()):
        try:
            w.write((line + "\n").encode())
        except:
            pass

async def handle_command(username: str, line: str):
	try:
		parts = shlex.split(line)
	except ValueError:
		return [("one", "ERROR")]

	match parts:
		case ["move", dx, dy]:
			x, y, encounter = game.move(username, int(dx), int(dy))
			res = [("one", f"MOVE {x} {y}")]
			if encounter is None:
				res.append(("one", "NO_ENCOUNTER"))
			else:
				name, hello = encounter
				res.append(("one", shlex.join(["ENCOUNTER", name, hello])))
			return res

		case ["addmon", name, hello, hp, x, y]:
			hp, x, y = int(hp), int(x), int(y)
			replaced = game.addmon(name, hello, hp, x, y)
			res = [
				("all", f"{username} added {name} with {hp} hp at ({x},{y})")
			]
			if replaced:
				res.append(("all", "Replaced old monster"))
			return res

		case ["attack", target, weapon, damage]:
			damage = int(damage)
			ok, dealt, hp_left = game.attack(username, damage, target)
			if not ok:
				return [("one", f"No {target} here")]
			if hp_left == 0:
				return [
					("all", f"{username} attacked {target} with {weapon}, damage {damage} hp"),
					("all", f"{target} died"),
				]
			return [
				("all", f"{username} attacked {target} with {weapon}, damage {damage} hp"),
				("all", f"{target} has {hp_left} hp"),
			]

		case _:
			return [("one", "ERROR")]

async def handle_client(reader, writer):
	username = None

	try:
		data = await reader.readline()
		if not data:
			return

		try:
			parts = shlex.split(data.decode().strip())
		except ValueError:
			writer.write(b"ERROR\n")
			return
		if len(parts) != 2 or parts[0] != "login":
			writer.write(b"ERROR\n")
			return

		username = parts[1]

		if username in game.players:
			writer.write(b"Username already taken\n")
			return

		game.players[username] = [0, 0]
		clients[username] = writer

		await broadcast(f"{username} entered the MUD")

		while True:
			data = await reader.readline()
			if not data:
				break

			line = data.decode().strip()
			response = await handle_command(username, line)

			for scope, msg in response:
				if scope == "one":
					writer.write((msg + "\n").encode())
				else:
					await broadcast(msg)

	finally:
		if username:
			clients.pop(username, None)
			game.players.pop(username, None)
			await broadcast(f"{username} left the MUD")

		writer.close()
		await writer.wait_closed()


async def main():
	server = await asyncio.start_server(handle_client, HOST, PORT)

	print(f"Server has been started on {HOST}:{PORT}")

	async with server:
		await server.serve_forever()


if __name__ == "__main__":
	asyncio.run(main())