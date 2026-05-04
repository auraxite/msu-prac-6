#!/usr/bin/env python3

from pathlib import Path


PROJECT = "wordcount"
LOCALE_DIR = Path("po")
LANG = "ru_RU.UTF-8"
MESSAGES_DIR = LOCALE_DIR / LANG / "LC_MESSAGES"
PO_FILE = MESSAGES_DIR / f"{PROJECT}.po"
MO_FILE = MESSAGES_DIR / f"{PROJECT}.mo"


def task_erase():
	return {
		"actions": [f"rm -f {MO_FILE}"],
	}


def task_dist():
	return {
		"actions": ["pyproject-build -s"],
		"task_dep": ["erase"],
	}


def task_mp():
	MESSAGES_DIR.mkdir(parents=True, exist_ok=True)
	return {
		"actions": [f"pybabel compile -D {PROJECT} -l {LANG} -i {PO_FILE} -d {LOCALE_DIR}"],
		"file_dep": [str(PO_FILE)],
		"targets": [str(MO_FILE)],
	}
