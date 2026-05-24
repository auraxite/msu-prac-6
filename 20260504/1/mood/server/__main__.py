"""Точка входа для запуска сервера."""

import asyncio

from mood.common.const import HOST, PORT

from .server import main


def serve(host: str = HOST, port: int = PORT) -> None:
	asyncio.run(main(host, port))


if __name__ == "__main__":
	serve()
