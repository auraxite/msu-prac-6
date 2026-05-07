"""Асинхронный сервер"""

import asyncio
import shlex

from .game import Game
from .i18n import RU, catalog, hp_phrase, tr
from .protocol import handle_command
from mood.common.const import HOST, PORT, WAITING_TIME


def expand(locale: str, part: str | tuple[str, dict]) -> str:
	if isinstance(part, str):
		return part
	msgid, kw = part
	kw = dict(kw)
	d = kw.get("direction")
	if isinstance(d, str) and d in {"right", "left", "up", "down"}:
		kw["direction"] = catalog.gettext(f"dir_{d}") if locale == RU else d
	for key in ("hp", "dmg"):
		n = kw.get(key)
		if isinstance(n, int):
			kw[key] = hp_phrase(locale, n)
	return tr(locale, msgid, **kw)


game = Game()
clients_writers = {}
client_locales: dict[str, str] = {}


async def broadcast(part: str | tuple[str, dict]):
	for username, w in list(clients_writers.items()):
		try:
			w.write((expand(client_locales.get(username, ""), part) + "\n").encode())
		except OSError:
			pass


async def send_line(writer: asyncio.StreamWriter, line: str) -> bool:
	try:
		writer.write((line + "\n").encode())
		return True
	except OSError:
		pass


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
	username = None

	try:
		data = await reader.readline()
		if not data:
			return

		try:
			parts = shlex.split(data.decode().strip())
		except ValueError:
			await send_line(writer, "ERROR")
			return

		if len(parts) != 2 or parts[0] != "login":
			await send_line(writer, "ERROR")
			return

		username = parts[1]

		if username in game.players:
			await send_line(writer, "Username already taken")
			return

		game.players[username] = [0, 0]
		clients_writers[username] = writer
		client_locales[username] = ""

		await broadcast(("%(username)s entered the MUD", {"username": username}))

		while True:
			data = await reader.readline()
			if not data:
				break

			line = data.decode().strip()
			response = await handle_command(game, username, line, client_locales)
			loc = client_locales.get(username, "")
			for scope, msg in response:
				if scope == "one":
					await send_line(writer, expand(loc, msg))
				else:
					await broadcast(msg)

	finally:
		if username:
			clients_writers.pop(username, None)
			client_locales.pop(username, None)
			game.players.pop(username, None)
			await broadcast(("%(username)s left the MUD", {"username": username}))

		writer.close()
		await writer.wait_closed()


async def notify_encounter(usernames: list[str], encounter: tuple[str, str]) -> None:
	name, hello = encounter
	message = shlex.join(["ENCOUNTER", name, hello])
	for username in usernames:
		writer = clients_writers.get(username)
		if writer is not None:
			await send_line(writer, message)


async def wander_monsters() -> None:
	while True:
		await asyncio.sleep(WAITING_TIME)
		moved = game.move_random_monster()
		if moved is None:
			continue

		name, direction, usernames, encounter = moved
		await broadcast(("%(name)s moved one cell %(direction)s", {"name": name, "direction": direction}))
		if usernames:
			await notify_encounter(usernames, encounter)


async def main(host: str = HOST, port: int = PORT) -> None:
	server = await asyncio.start_server(handle_client, host, port)
	wander_task = asyncio.create_task(wander_monsters())

	print(f"\nServer has been started on {host}:{port}")

	try:
		async with server:
			await server.serve_forever()
	finally:
		wander_task.cancel()
		await asyncio.gather(wander_task, return_exceptions=True)


def serve(host: str = HOST, port: int = PORT) -> None:
	asyncio.run(main(host, port))
