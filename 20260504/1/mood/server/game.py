"""Состояние и механики MUD."""

import random

from mood.common.const import SIZE


DIRECTIONS = {
	"right": (1, 0),
	"left": (-1, 0),
	"up": (0, -1),
	"down": (0, 1),
}


class Game:
	"""Состояние игры и её механика."""

	def __init__(self) -> None:
		"""Инициализировать пустую игру."""
		self.players = {} # username -> [x, y]
		self.monsters = {} # (x, y) -> (name, hello, hp)
		self.moving_monsters = True

	def wrap_coord(self, n: int) -> int:
		"""Обернуть координату."""
		return n % SIZE

	def encounter(self, x: int, y: int) -> tuple[str, str] | None:
		"""Проверить, есть ли монстр в клетке."""
		key = (x, y)
		if key in self.monsters:
			name, hello, hp = self.monsters[key]
			return name, hello
		return None

	def move(self, username: str, dx: int, dy: int) -> tuple[int, int, tuple[str, str] | None]:
		"""Двигать игрока. Вернуть его новые координаты и возможную встречу."""
		x, y = self.players[username]
		x = self.wrap_coord(x + dx)
		y = self.wrap_coord(y + dy)
		self.players[username] = [x, y]
		encounter = self.encounter(x, y)
		return x, y, encounter

	def addmon(self, name: str, hello: str, hp: int, x: int, y: int) -> bool:
		"""Добавить монстра в клетку. Вернуть True, если там уже был монстр."""
		key = (x, y)
		replaced = key in self.monsters
		self.monsters[key] = (name, hello, hp)
		return replaced

	def attack(self, username: str, damage: int, target: str) -> tuple[bool, int, int]:
		"""Атаковать монстра в клетке. Вернуть (успех, нанесённый урон, оставшееся hp)."""
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

	def players_at(self, x: int, y: int) -> list[str]:
		"""Вернуть список игроков в клетке."""
		return [
			username
			for username, coords in self.players.items()
			if coords == [x, y]
		]

	def set_movemonsters(self, enabled: bool) -> str:
		"""Включить/выключить режим бродячих монстров."""
		self.moving_monsters = enabled
		return f"Moving monsters: {'on' if enabled else 'off'}"

	def move_random_monster(self) -> tuple[str, str, list[str], tuple[str, str]] | None:
		"""Двигать случайного монстра в случайном направлении."""
		if not self.moving_monsters:
			return None

		if not self.monsters:
			return None

		positions = list(self.monsters)
		directions = list(DIRECTIONS.items())
		has_move = any(
			(
				self.wrap_coord(x + dx),
				self.wrap_coord(y + dy),
			) not in self.monsters
			for x, y in positions
			for direction, (dx, dy) in directions
		)
		if not has_move:
			return None

		while True:
			x, y = random.choice(positions)
			direction, (dx, dy) = random.choice(directions)
			new_x = self.wrap_coord(x + dx)
			new_y = self.wrap_coord(y + dy)
			new_key = (new_x, new_y)

			if new_key in self.monsters:
				continue

			monster = self.monsters.pop((x, y))
			self.monsters[new_key] = monster
			name, hello, _hp = monster
			return name, direction, self.players_at(new_x, new_y), (name, hello)
