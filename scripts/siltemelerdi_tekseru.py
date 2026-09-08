#!/usr/bin/env python3
"""Markdown файлдарындағы қатысты сілтемелердің бар-жоғын тексереді.

Шеберліктер бір-біріне және `references/` файлдарына сілтеме жасайды.
Файл атын өзгерткенде сілтеме үнсіз бұзылады, ал модель жоқ файлды оқуға
тырысып, керекті ережені көрмей қалады. Бұл скрипт соны CI-да ұстайды.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

TUBIR = Path(__file__).resolve().parents[1]
SILTEME = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def tekseru() -> int:
    qateler: list[str] = []
    tekserilgen = 0

    for md in sorted(TUBIR.rglob("*.md")):
        if any(bolim in md.parts for bolim in (".git", "node_modules")):
            continue
        mati = md.read_text(encoding="utf-8")
        for siltem in SILTEME.findall(mati):
            if siltem.startswith(("http://", "https://", "#", "mailto:")):
                continue
            tekserilgen += 1
            nysana = (md.parent / siltem.split("#", 1)[0]).resolve()
            if not nysana.exists():
                qateler.append(
                    f"{md.relative_to(TUBIR)}: «{siltem}» → файл жоқ"
                )

    if qateler:
        print(f"Бұзылған сілтеме: {len(qateler)}\n", file=sys.stderr)
        for q in qateler:
            print(f"  {q}", file=sys.stderr)
        return 1

    print(f"Барлық қатысты сілтеме дұрыс ({tekserilgen} тексерілді).")
    return 0


if __name__ == "__main__":
    raise SystemExit(tekseru())
