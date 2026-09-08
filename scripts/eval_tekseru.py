#!/usr/bin/env python3
"""`evals/evals.json` файлдарының құрылымын тексереді.

Eval — шеберліктің дұрыс жағдайда қосылатынын және дұрыс ұстанатынын
сипаттайтын жағдайлар жиыны. Оны модельмен жүргізу бөлек іс, ал бұл
скрипт файлдың өзін тексереді: құрылымы дұрыс па, атауы бумамен сәйкес пе,
мазмұны бос емес пе.

Ат ASCII болуы міндетті. Бұл — тақырыпқа сай ереже: бандлдың өзі
кирилл мен латынның араласуын қате санайды, сондықтан өз файлдарында
да ондай ат болмауы керек.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TUBIR = Path(__file__).resolve().parents[1]
AT_ULGI = re.compile(r"^[a-z0-9_]+$")


def tekseru() -> int:
    qateler: list[str] = []
    barlyq_eval = 0
    skildter = sorted(TUBIR.glob("skills/*/"))

    for buma in skildter:
        atau = buma.name
        jol = buma / "evals" / "evals.json"
        if not jol.exists():
            qateler.append(f"{atau}: evals/evals.json жоқ")
            continue

        try:
            d = json.loads(jol.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            qateler.append(f"{atau}: JSON оқылмады — {e}")
            continue

        if d.get("skill") != atau:
            qateler.append(
                f"{atau}: «skill» өрісі «{d.get('skill')}» — бума атымен сәйкес емес"
            )

        evaldar = d.get("evals")
        if not isinstance(evaldar, list) or not evaldar:
            qateler.append(f"{atau}: «evals» тізімі бос немесе жоқ")
            continue

        korilgen: set[str] = set()
        for i, e in enumerate(evaldar):
            belgi = f"{atau}[{i}]"
            at = e.get("name", "")
            if not at:
                qateler.append(f"{belgi}: «name» жоқ")
            elif not AT_ULGI.match(at):
                qateler.append(
                    f"{belgi}: «{at}» — ат тек ASCII кіші әріп, цифр және "
                    "астыңғы сызықтан тұруы керек (кирилл әрпі кіріп кетпесін)"
                )
            elif at in korilgen:
                qateler.append(f"{belgi}: «{at}» аты қайталанған")
            else:
                korilgen.add(at)

            if not e.get("input"):
                qateler.append(f"{belgi}: «input» жоқ")
            kutilgen = e.get("expect")
            if not isinstance(kutilgen, list) or not kutilgen:
                qateler.append(f"{belgi}: «expect» тізімі бос немесе жоқ")
            barlyq_eval += 1

    if qateler:
        print(f"Eval қателері: {len(qateler)}\n", file=sys.stderr)
        for q in qateler:
            print(f"  {q}", file=sys.stderr)
        return 1

    print(f"Барлық eval дұрыс ({len(skildter)} шеберлік, {barlyq_eval} жағдай).")
    return 0


if __name__ == "__main__":
    raise SystemExit(tekseru())
