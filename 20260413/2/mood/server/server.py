"""Async server for the MUD game"""

import asyncio
import shlex

from .game import Game
from .protocol import handle_command
from mood.common.const import HOST, PORT, WAITING_TIME

game = Game()
clients = {}


async def broadcast(line: str):
	for w in list(clients.values()):
		try:
			w.write((line + "\n").encode())
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
		clients[username] = writer

		await broadcast(f"{username} entered the MUD")

		while True:
			data = await reader.readline()
			if not data:
				break

			line = data.decode().strip()
			response = await handle_command(game, username, line)

			for scope, msg in response:
				if scope == "one":
					await send_line(writer, msg)
				else:
					await broadcast(msg)

	finally:
		if username:
			clients.pop(username, None)
			game.players.pop(username, None)
			await broadcast(f"{username} left the MUD")

		writer.close()
		await writer.wait_closed()

async def notify_encounter(usernames: list[str], encounter: tuple[str, str]) -> None:
	name, hello = encounter
	message = shlex.join(["ENCOUNTER", name, hello])
	for username in usernames:
		writer = clients.get(username)
		if writer is not None:
			await send_line(writer, message)


async def wander_monsters() -> None:
	while True:
		await asyncio.sleep(WAITING_TIME)
		moved = game.move_random_monster()
		if moved is None:
			continue

		name, direction, usernames, encounter = moved
		await broadcast(f"{name} moved one cell {direction}")
		if usernames:
			await notify_encounter(usernames, encounter)


async def main() -> None:
	server = await asyncio.start_server(handle_client, HOST, PORT)
	wander_task = asyncio.create_task(wander_monsters())

	print(f"Server has been started on {HOST}:{PORT}")

	try:
		async with server:
			await server.serve_forever()
	finally:
		wander_task.cancel()
		await asyncio.gather(wander_task, return_exceptions=True)
