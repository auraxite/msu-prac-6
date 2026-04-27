#!/usr/bin/env python3

def task_docs():
	"""Create documentation"""

	return {
		"actions": ["sphinx-build -M html . docs/build"]
	}

def ask_erase():
	"""Clear all junk"""

	return {
		"actions": ["rm -rf doc/build"]
	}