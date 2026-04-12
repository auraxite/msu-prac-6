from mood.common.const import SIZE


class Game:
	def __init__(self) -> None:
		self.players = {} # username -> [x, y]
		self.monsters = {} # (x, y) -> (name, hello, hp)

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
