import multiprocessing
import socket
import time
import unittest

from mood.server.server import serve


HOST = "127.0.0.1"
PORT = 1337


class TestServerCommands(unittest.TestCase):
	def setUp(self) -> None:
		self.proc = multiprocessing.Process(target=serve, args=(HOST, PORT))
		self.proc.start()
		time.sleep(1)

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((HOST, PORT))
		self.stream = self.sock.makefile("r", encoding="utf-8")
		self.send_command("login tester")
		self.read_line()

		self.send_command("movemonsters off")
		reply = self.read_line()
		self.assertEqual(reply, "Moving monsters: off")

	def tearDown(self) -> None:
		self.stream.close()
		self.sock.close()
		self.proc.terminate()
		self.proc.join(timeout=2)
		if self.proc.is_alive():
			self.proc.kill()
			self.proc.join(timeout=2)
		time.sleep(0.1)

	def send_command(self, command: str) -> None:
		self.sock.sendall((command + "\n").encode())

	def read_line(self) -> str:
		return self.stream.readline().strip()

	def test_1(self) -> None:
		self.send_command("addmon tux 'Hello :)' 10 1 0")
		self.assertEqual(
			self.read_line(),
			"tester added tux with 10 hp at (1,0)",
		)

	def test_2(self) -> None:
		self.send_command("addmon tux 'Hello :)' 10 1 0")
		self.read_line()
		self.send_command("move 1 0")
		self.assertEqual(self.read_line(), "MOVE 1 0")
		self.assertEqual(self.read_line(), "ENCOUNTER tux 'Hello :)'")

	def test_3(self) -> None:
		self.send_command("addmon tux 'Hello :)' 10 1 0")
		self.read_line()
		self.send_command("move 1 0")
		self.read_line()
		self.read_line()
		self.send_command("attack tux sword 10")
		self.assertEqual(
			self.read_line(),
			"tester attacked tux with sword, damage 10 hp",
		)
		self.assertEqual(self.read_line(), "tux died")


if __name__ == "__main__":
	unittest.main()
