"""Languages."""

import gettext
import os

RU = "ru_RU.UTF8"
catalog = gettext.translation(
	"messages",
	os.path.join(os.path.dirname(__file__), "locale"),
	languages=["ru_RU"],
	fallback=True,
)


def tr(locale: str, msgid: str, **kwargs) -> str:
	s = catalog.gettext(msgid) if locale == RU else msgid
	return s % kwargs if kwargs else s


def hp_phrase(locale: str, n: int) -> str:
	if locale != RU:
		return f"{n} hp"
	s = catalog.ngettext("%(n)d hp", "%(n)d hp", n)
	return s % {"n": n}
