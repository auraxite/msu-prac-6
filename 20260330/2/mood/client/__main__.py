import sys

from .shell import Shell


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m mood.client <username>")
        raise SystemExit(1)
    Shell(sys.argv[1]).cmdloop()


if __name__ == "__main__":
    main()