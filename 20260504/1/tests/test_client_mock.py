import cowsay
import shlex
import unittest
from unittest.mock import MagicMock, patch

from mood.client.shell import Shell


MONSTER = "tux" if "tux" in cowsay.list_cows() else sorted(cowsay.list_cows())[0]


class TestClientProtocolConversion(unittest.TestCase):
	def run_session(self, commands):
		fake_socket = MagicMock()
		fake_thread = MagicMock()
		fake_thread.start.return_value = None

		with (
			patch("mood.client.shell.socket.socket", return_value=fake_socket),
			patch("mood.client.shell.threading.Thread", return_value=fake_thread),
			patch("builtins.input", side_effect=[*commands, "quit"]),
			patch("builtins.print") as mock_print,
		):
			shell = Shell("tester")
			shell.intro = ""
			shell.cmdloop()

		sent = [
			args[0].decode().strip()
			for args, _kwargs in fake_socket.sendall.call_args_list
		]
		return sent[1:], mock_print

	def test_addmon_1(self):
		sent, _ = self.run_session([f"addmon {MONSTER} hello hi hp 10 coords 1 0"])
		expected = shlex.join(["addmon", MONSTER, "hi", "10", "1", "0"])
		self.assertEqual(sent, [expected])

	def test_addmon_2(self):
		hello = "Hello :)"
		sent, _ = self.run_session([f'addmon {MONSTER} hello "{hello}" hp 25 coords 2 3'])
		expected = shlex.join(["addmon", MONSTER, hello, "25", "2", "3"])
		self.assertEqual(sent, [expected])

	def test_attack_1(self):
		sent, _ = self.run_session([f"attack {MONSTER}"])
		expected = shlex.join(["attack", MONSTER, "sword", "10"])
		self.assertEqual(sent, [expected])

	def test_attack_2(self):
		sent, _ = self.run_session([f"attack {MONSTER} with axe"])
		expected = shlex.join(["attack", MONSTER, "axe", "20"])
		self.assertEqual(sent, [expected])

	def test_attack_3(self):
		sent, mock_print = self.run_session([f"attack {MONSTER} with"])
		self.assertEqual(sent, [])
		mock_print.assert_any_call("Invalid arguments")


if __name__ == "__main__":
	unittest.main()
