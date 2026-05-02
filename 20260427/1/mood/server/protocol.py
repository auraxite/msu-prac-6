"""Парсинг комманд"""

import shlex


async def handle_command(game, username: str, line: str, locales: dict[str, str]):
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
				(
					"all",
					(
						"%(username)s added %(name)s with %(hp)s at (%(x)d,%(y)d)",
						{"username": username, "name": name, "hp": hp, "x": x, "y": y},
					),
				)
			]
			if replaced:
				res.append(("all", ("Replaced old monster", {})))
			return res

		case ["attack", target, weapon, damage]:
			damage = int(damage)
			ok, dealt, hp_left = game.attack(username, damage, target)
			if not ok:
				return [("one", ("No %(target)s here", {"target": target}))]
			if hp_left == 0:
				return [
					(
						"all",
						(
							"%(username)s attacked %(target)s with %(weapon)s, damage %(dmg)s",
							{
								"username": username,
								"target": target,
								"weapon": weapon,
								"dmg": dealt,
							},
						),
					),
					("all", ("%(target)s died", {"target": target})),
				]
			return [
				(
					"all",
					(
						"%(username)s attacked %(target)s with %(weapon)s, damage %(dmg)s",
						{
							"username": username,
							"target": target,
							"weapon": weapon,
							"dmg": dealt,
						},
					),
				),
				(
					"all",
					("%(target)s has %(hp)s", {"target": target, "hp": hp_left}),
				),
			]

		case ["sayall", *message_parts]:
			if not message_parts:
				return [("one", "ERROR")]

			message = " ".join(message_parts)
			return [("all", f"{username}: {message}")]

		case ["movemonsters", "on"]:
			return [("one", game.set_movemonsters(True))]
		case ["movemonsters", "off"]:
			return [("one", game.set_movemonsters(False))]

		case ["locale", locale_name]:
			locales[username] = locale_name
			return [("one", ("Set up locale: %(locale_name)s", {"locale_name": locale_name}))]

		case _:
			return [("one", "ERROR")]
