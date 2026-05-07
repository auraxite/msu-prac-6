"""Автоматизация сборки проекта"""

import shutil
from pathlib import Path

from doit.task import clean_targets

DOIT_CONFIG = {"default_tasks": ["i18n", "test", "html", "sdist", "wheel"]}

BUILD_DIR = Path("build")
DOCS_BUILD_DIR = Path("docs/build")
DIST_DIR = Path("dist")
SDIST_FILE = DIST_DIR / "mood-0.1.tar.gz"
WHEEL_FILE = DIST_DIR / "mood-0.1-py3-none-any.whl"
EGG_INFO_DIR = Path("mood.egg-info")
POT_FILE = Path("mood/server/locale/messages.pot")
PO_FILE = Path("mood/server/locale/ru_RU/LC_MESSAGES/messages.po")
MO_FILE = Path("mood/server/locale/ru_RU/LC_MESSAGES/messages.mo")


def clean_build() -> None:
	for path in (DOCS_BUILD_DIR, DIST_DIR, BUILD_DIR, EGG_INFO_DIR):
		if path.exists():
			shutil.rmtree(path)
	for path in Path(".").rglob("__pycache__"):
		if path.is_dir():
			shutil.rmtree(path)

# region i18n
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
# endregion

def task_html():
	return {
		"actions": ["cd docs && sphinx-build -M html . build"],
		"file_dep": 
			[str(p) for p in Path("docs").glob("**/*.rst")] + \
			[str(p) for p in Path("mood").glob("**/*.py")],
		"targets": [str(DOCS_BUILD_DIR / "html" / "index.html")],
		"clean": [clean_targets, clean_build],
	}


def task_test():
	return {
		"actions": ["python3 -m unittest discover -s tests -p 'test_*.py' -v"],
		"file_dep":
			[str(p) for p in Path("tests").glob("test_*.py")] + \
			[str(p) for p in Path("mood").glob("**/*.py")],
		"task_dep": ["i18n"],
		"clean": [clean_targets],
	}


def task_sdist():
	return {
		"actions": ["python3 -m build --sdist"],
		"file_dep":
			["pyproject.toml", "dodo.py"] + \
			[str(p) for p in Path("mood").glob("**/*") if p.is_file()],
		"targets": [str(SDIST_FILE)],
		"task_dep": ["html", "i18n"],
		"clean": [clean_targets, clean_build],
	}


def task_wheel():
	return {
		"actions": ["python3 -m build --wheel"],
		"file_dep":
			["pyproject.toml", "dodo.py"] + \
			[str(p) for p in Path("mood").glob("**/*") if p.is_file()],
		"targets": [str(WHEEL_FILE)],
		"task_dep": ["html", "i18n"],
		"clean": [clean_targets, clean_build],
	}
