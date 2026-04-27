#!/usr/bin/env python3

from pathlib import Path
from zipfile import ZipFile

DOIT_CONFIG = {"default_tasks": ["docs"]}


def task_docs():
	"""Create documentation"""

	rstpy = list(Path(".").glob("**/*.rst")) + \
		list(Path(".").glob("**/*.py"))
	ext = {"html": "html", "text": "txt"}
	
	for typ in ("html", "txt"):
		yield {
			"name": f"{typ} doc",
			"actions": [f"cd docs && sphinx-build -M {typ} . build"],
			"targets": [f"docs/build/index.{ext[typ]}"],
			"file_dep": rstpy,
		}


def task_erase():
	"""Clear all junk"""

	return {
		"actions": ["rm -rf docs/build* .zip"]
	}


def task_zip():
	"""Create ZIP archive of docs"""

	def create_zip(filename, files):
		with ZipFile(filename, "w") as zf:
			for f in files:
				zf.write(f)

	files = list(Path("docs/build/html").glob("**"))

	return {
		"actions": [(create_zip, ["docs.zip", files])],
		"task_dep": ["docs"]
	}
