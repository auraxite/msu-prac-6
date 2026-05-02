"""Автоматизация сборки проекта"""

import shutil
from pathlib import Path

from doit.task import clean_targets

DOIT_CONFIG = {"default_tasks": ["html"]}

DOCS_DIR = Path("docs")
DOCS_BUILD_DIR = DOCS_DIR / "build"
POT_FILE = Path("mood/server/locale/messages.pot")
PO_FILE = Path("mood/server/locale/ru_RU/LC_MESSAGES/messages.po")
MO_FILE = Path("mood/server/locale/ru_RU/LC_MESSAGES/messages.mo")


def clean_docs_build() -> None:
	if DOCS_BUILD_DIR.exists():
		shutil.rmtree(DOCS_BUILD_DIR)


def task_i18n_pot():
	py_sources = [str(p) for p in Path("mood").glob("**/*.py")]
	return {
		"actions": [
			"xgettext --from-code=UTF-8 --language=Python "
			"--keyword=tr:2 --keyword=ngettext:1,2,3 "
			"--output=mood/server/locale/messages.pot "
			+ " ".join(py_sources)
		],
		"file_dep": py_sources,
		"targets": [str(POT_FILE)],
		"clean": [clean_targets],
	}


def task_i18n_po():
	return {
		"actions": [
			"msgmerge --update --backup=none "
			"mood/server/locale/ru_RU/LC_MESSAGES/messages.po "
			"mood/server/locale/messages.pot"
		],
		"file_dep": [str(POT_FILE)],
		"targets": [str(PO_FILE)],
		"task_dep": ["i18n_pot"],
		"clean": [clean_targets],
	}


def task_i18n_mo():
	return {
		"actions": [
			"msgfmt -o mood/server/locale/ru_RU/LC_MESSAGES/messages.mo "
			"mood/server/locale/ru_RU/LC_MESSAGES/messages.po"
		],
		"file_dep": [str(PO_FILE)],
		"targets": [str(MO_FILE)],
		"task_dep": ["i18n_po"],
		"clean": [clean_targets],
	}


def task_i18n():
	return {
		"actions": [],
		"task_dep": ["i18n_pot", "i18n_po", "i18n_mo"],
	}


def task_html():
	return {
		"actions": ["cd docs && sphinx-build -M html . build"],
		"file_dep": [str(p) for p in DOCS_DIR.glob("**/*.rst")] + [str(p) for p in Path("mood").glob("**/*.py")],
		"targets": [str(DOCS_BUILD_DIR / "html" / "index.html")],
		"clean": [clean_targets, clean_docs_build],
	}


def task_test():
	return {
		"actions": ["python3 -m unittest discover -s tests -p 'test_*.py' -v"],
		"file_dep": [str(p) for p in Path("tests").glob("test_*.py")],
		"task_dep": ["i18n"],
		"clean": [clean_targets],
	}
