import os
import sys
from pathlib import Path


def git_dir(repo: Path) -> str:
    repo = str(repo.resolve())
    dotgit = os.path.join(repo, ".git")
    if os.path.isdir(dotgit):
        return dotgit
    if os.path.isdir(os.path.join(repo, "objects")) and os.path.isdir(os.path.join(repo, "refs")):
        return repo
    raise "Not a git repo"


def list_branches(gd: str) -> None:
    heads = os.path.join(gd, "refs", "heads")
    if not os.path.isdir(heads):
        return
    for root, _, files in os.walk(heads):
        for f in sorted(files):
            full = os.path.join(root, f)
            print(os.path.relpath(full, heads))


def run(argv: list[str]) -> None:
    gd = git_dir(Path(argv[1]))
    list_branches(gd)


if __name__ == "__main__":
    run(sys.argv)