import asyncio
import shlex

from .game import Game
from .protocol import handle_command
from mood.common.const import HOST, PORT


game = Game()
clients = {}


async def broadcast(line: str):
	for w in list(clients.values()):
		try:
			w.write((line + "\n").encode())
		except OSError:
			pass


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
			response = await handle_command(game, username, line)

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
