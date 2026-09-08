#!/usr/bin/env python3
"""Әр SKILL.md файлында дұрыс frontmatter бар-жоғын тексереді.

`name` мен `description` болмаса, шеберлік мүлдем қосылмайды — қате үнсіз
өтеді, ал пайдаланушы «неге істемейді?» деп отырады.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

TUBIR = Path(__file__).resolve().parents[1]
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

# Threads сипаттамасын қысқа ұстау керек: ол модельдің контексінде
# үнемі тұрады.
DESC_MAX = 1024


def tekseru() -> int:
    qateler: list[str] = []
    tabylgan = 0

    joldar = [TUBIR / "SKILL.md", *sorted(TUBIR.glob("skills/*/SKILL.md"))]
    for jol in joldar:
        atau = jol.relative_to(TUBIR)
        if not jol.exists():
            qateler.append(f"{atau}: файл жоқ")
            continue
        tabylgan += 1
        m = FRONTMATTER.match(jol.read_text(encoding="utf-8"))
        if not m:
            qateler.append(f"{atau}: frontmatter жоқ немесе файл басында тұрған жоқ")
            continue

        oris = dict(
            re.findall(r"^(name|description):\s*(.+)$", m.group(1), re.MULTILINE)
        )
        for kilt in ("name", "description"):
            if kilt not in oris:
                qateler.append(f"{atau}: «{kilt}» өрісі жоқ")

        at = oris.get("name", "")
        if at and jol.parent.name != "." and jol != TUBIR / "SKILL.md":
            if at != jol.parent.name:
                qateler.append(
                    f"{atau}: name «{at}» бума атымен «{jol.parent.name}» сәйкес емес"
                )

        sipattama = oris.get("description", "")
        if len(sipattama) > DESC_MAX:
            qateler.append(f"{atau}: description тым ұзын ({len(sipattama)} > {DESC_MAX})")

    if qateler:
        print(f"Frontmatter қателері: {len(qateler)}\n", file=sys.stderr)
        for q in qateler:
            print(f"  {q}", file=sys.stderr)
        return 1

    print(f"Барлық frontmatter дұрыс ({tabylgan} файл).")
    return 0


if __name__ == "__main__":
    raise SystemExit(tekseru())
