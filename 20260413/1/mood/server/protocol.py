"""Command parsing for the MUD"""

import shlex


async def handle_command(game, username: str, line: str):
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
					("all", f"{username} attacked {target} with {weapon}, damage {dealt} hp"),
					("all", f"{target} died"),
				]
			return [
				("all", f"{username} attacked {target} with {weapon}, damage {dealt} hp"),
				("all", f"{target} has {hp_left} hp"),
			]

		case ["sayall", *message_parts]:
			if not message_parts:
				return [("one", "ERROR")]

			message = " ".join(message_parts)
			return [("all", f"{username}: {message}")]

		case _:
			return [("one", "ERROR")]
