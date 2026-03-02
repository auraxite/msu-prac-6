from shlex import join, split


def main() -> None:
    while True:
        s = input(">>> ").strip()

        if s.lower() == 'q':
            break

        parts = split(s)
        print(s, len(parts), parts)
        cmd = join(parts)
        print(cmd)


if __name__ == "__main__":
    main()