from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))

project = "MUD"
author = "Auraxite"
copyright = "2026, Auraxite"

extensions = [
    "sphinx.ext.autodoc",
]

templates_path = ["_templates"]
exclude_patterns = ["_build"]

language = "ru"

autodoc_member_order = "bysource"
autoclass_content = "both"

html_theme = "alabaster"
