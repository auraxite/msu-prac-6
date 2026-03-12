import cmd
from shlex import split
import calendar


class Calendar(cmd.Cmd):
    prompt = "==> "

    def do_prmonth(self, arg):
        """Print a month’s calendar as returned by formatmonth()."""

        args = arg.split()
        print(calendar.prmonth(int(args[0]), int(args[1])))

    def do_pryear(self, arg):
        """Print the calendar for an entire year as returned by formatyear()."""

        args = arg.split()
        print(calendar.pryear(int(args[0])))

    def do_exit(self):
        """exit"""

        return 1


if __name__ == "__main__":
    Calendar().cmdloop()