import os
import sys
from pathlib import Path
from zlib import decompress


def git_dir(repo: Path) -> str:
    repo = str(repo.resolve())
    dotgit = os.path.join(repo, ".git")
    if os.path.isdir(dotgit):
        return dotgit
    if os.path.isdir(os.path.join(repo, "objects")) and os.path.isdir(os.path.join(repo, "refs")):
        return repo
    raise Exception("Not a git repo")


def list_branches(gd: str) -> None:
    heads = os.path.join(gd, "refs", "heads")
    if not os.path.isdir(heads):
        return
    for root, _, files in os.walk(heads):
        for f in sorted(files):
            full = os.path.join(root, f)
            print(os.path.relpath(full, heads))


def read_object(gd: str, sha: str) -> tuple[str, bytes]:
    sha = sha.strip()
    obj_path = os.path.join(gd, "objects", sha[:2], sha[2:])
    raw = open(obj_path, "rb").read()
    data = decompress(raw)
    header, _, body = data.partition(b"\x00")
    obj_type = header.decode("utf-8", errors="replace").split()[0]
    return obj_type, body


def branch_head_sha(gd: str, branch: str) -> str:
    ref_path = os.path.join(gd, "refs", "heads", branch)
    if not os.path.isfile(ref_path):
        raise Exception("Branch not found")
    return open(ref_path, "r", encoding="utf-8", errors="replace").read().strip()


def print_last_commit(gd: str, branch: str) -> None:
    head = branch_head_sha(gd, branch)
    obj_type, body = read_object(gd, head)
    if obj_type != "commit":
        raise Exception("Branch head is not a commit")

    text = body.decode("utf-8", errors="replace")
    header, _, message = text.partition("\n\n")

    tree_sha = ""
    parents = []
    author = ""
    committer = ""

    for line in header.splitlines():
        if line.startswith("tree "):
            tree_sha = line.split()[1]
        elif line.startswith("parent "):
            parents.append(line.split()[1])
        elif line.startswith("author "):
            v = line[len("author "):]
            end = v.find(">")
            author = v[:end + 1].strip() if end != -1 else v.strip()
        elif line.startswith("committer "):
            v = line[len("committer "):]
            end = v.find(">")
            committer = v[:end + 1].strip() if end != -1 else v.strip()

    print(f"tree {tree_sha}")
    for p in parents:
        print(f"parent {p}")
    print(f"author {author}")
    print(f"committer {committer}")
    print()
    print(message, end="")
    if message and not message.endswith("\n"):
        print()


def get_tree_sha_of_branch(gd: str, branch: str) -> str:
    head = branch_head_sha(gd, branch)
    obj_type, body = read_object(gd, head)
    if obj_type != "commit":
        raise Exception("Branch head is not a commit")

    text = body.decode("utf-8", errors="replace")
    for line in text.splitlines():
        if line.startswith("tree "):
            return line.split()[1]
        if line == "":
            break
    raise Exception("Commit has no tree")


def parse_tree(body: bytes):
    i = 0
    while i < len(body):
        j = body.find(b" ", i)
        mode = body[i:j].decode("utf-8", errors="replace")
        k = body.find(b"\x00", j + 1)
        name = body[j + 1:k].decode("utf-8", errors="replace")
        sha_bytes = body[k + 1:k + 21]
        sha = sha_bytes.hex()
        i = k + 21

        kind = "tree" if mode == "40000" else "blob" # mode == "40000" means dir
        yield kind, sha, name


def print_tree(gd: str, tree_sha: str) -> None:
    obj_type, body = read_object(gd, tree_sha)
    if obj_type != "tree":
        raise Exception("Not a tree object")
    for kind, sha, name in parse_tree(body):
        print(f"{kind} {sha}    {name}")


def run(argv: list[str]) -> None:
    gd = git_dir(Path(argv[1]))
    if len(argv) == 2:
        list_branches(gd)
    elif len(argv) == 3:
        branch = argv[2]
        print_last_commit(gd, branch)
        print()
        tree_sha = get_tree_sha_of_branch(gd, branch)
        print_tree(gd, tree_sha)
    else:
        raise Exception("Usage: python3 prog.py <repo> <branch>")


if __name__ == "__main__":
    run(sys.argv)