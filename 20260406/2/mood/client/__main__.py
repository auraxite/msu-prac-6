import sys

from .shell import Shell


def main() -> None:
	if len(sys.argv) == 2:
		Shell(sys.argv[1]).cmdloop()
		return

	if len(sys.argv) == 4 and sys.argv[2] == "--file":
		Shell(sys.argv[1]).run_file(sys.argv[3])
		return

	print("Usage: python -m mood.client <username> [--file <filename>]")
	raise SystemExit(1)


if __name__ == "__main__":
	main()
