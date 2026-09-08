"""Дауысты үндестігі: қосымша сөзге дұрыс жалғанған ба?

Қазақ тілінде қосымшаның дауыстысы сөздің СОҢҒЫ буынының дауыстысына
қарай таңдалады. Кірме сөзге жалғағанда бұл ереже жиі бұзылады, өйткені
адам түпнұсқа тілдің дыбысталуына сүйенеді:

    ❌ дедлайнге   ✅ дедлайнға   (соңғы дауысты «а» — жуан)
    ❌ релизға     ✅ релизге     (соңғы дауысты «и» — жіңішке)
    ❌ стартапке   ✅ стартапқа   (соңғы дауысты «а» — жуан)

Не тексереді: тек ДАУЫСТЫ үндестігі. Дауыссыз үндестігі (-ға/-қа, -дан/-тан
таңдауы) бөлек ереже, оның ерекшелігі көп, сондықтан мұнда тексерілмейді.

Сенімділігі: ереже тұрақты, бірақ қосымшаға ұқсап аяқталатын түбір сөздер
бар (жалқы есімдер, кірме сөздер). Сондықтан барлық белгі «кеңес»
деңгейінде беріледі — үкім емес, қарап шығуға ұсыныс.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# Жуан (артқы қатар) дауыстылар.
JUAN = set("аоұы")
# Жіңішке (алдыңғы қатар) дауыстылар. «и» кірме сөздерде жіңішке ұстанады.
JINISHKE = set("әөүіеи")
# «у» кірме сөздерде екі түрлі ұстанады (институтқа, бірақ универсиетке),
# сондықтан оны соңғы дауысты етіп алған сөзді тексермейміз.
KUMANDI = set("у")

DAUYSTY = JUAN | JINISHKE | KUMANDI

# Қосымша жұптары: (жуан нұсқасы, жіңішке нұсқасы).
# Тек екі және одан көп таңбалы қосымшалар — бір таңбалысы тым көп
# жалған белгі береді.
JUPTAR: list[tuple[str, str]] = [
    ("дың", "дің"), ("тың", "тің"), ("ның", "нің"),   # ілік септік
    ("дан", "ден"), ("тан", "тен"), ("нан", "нен"),   # шығыс септік
    ("лар", "лер"), ("дар", "дер"), ("тар", "тер"),   # көптік
    ("ға", "ге"), ("қа", "ке"),                       # барыс септік
    ("ды", "ді"), ("ты", "ті"), ("ны", "ні"),         # табыс септік
    ("да", "де"), ("та", "те"),                       # жатыс септік
]
# Ұзынынан қысқасына қарай тексереміз, әйтпесе «дан» «да»-мен шатасады.
_RETPEN = sorted(JUPTAR, key=lambda j: -len(j[0]))

SOZ = re.compile(r"[а-яёәғқңөұүһі]+", re.IGNORECASE | re.UNICODE)


@dataclass
class Undestik:
    soz: str
    qosymsha: str
    kutilgen: str
    tuzetilgen: str
    songy_dauysty: str

    def __str__(self) -> str:
        return (
            f"«{self.soz}» — соңғы дауыстысы «{self.songy_dauysty}» "
            f"({'жуан' if self.songy_dauysty in JUAN else 'жіңішке'}), "
            f"сондықтан «-{self.kutilgen}» күтіледі.\n"
            f"    → {self.tuzetilgen}"
        )


def _songy_dauysty(tubir: str) -> str | None:
    for tanba in reversed(tubir):
        if tanba in DAUYSTY:
            return tanba
    return None


def tekseru(mati: str) -> list[Undestik]:
    """Мәтіндегі үндестік бұзылған сөздерді табады."""
    tabylgan: list[Undestik] = []

    for m in SOZ.finditer(mati):
        soz = m.group()
        toment = soz.lower()

        for juan, jinishke in _RETPEN:
            for qosymsha, kutilgen_jup in ((juan, jinishke), (jinishke, juan)):
                if not toment.endswith(qosymsha):
                    continue
                tubir = toment[: -len(qosymsha)]
                # Түбір тым қысқа болса, бұл қосымша емес, түбірдің өзі.
                if len(tubir) < 2:
                    break

                songy = _songy_dauysty(tubir)
                if songy is None or songy in KUMANDI:
                    break

                turi_juan = songy in JUAN
                qosymsha_juan = qosymsha == juan
                if turi_juan != qosymsha_juan:
                    tabylgan.append(
                        Undestik(
                            soz=soz,
                            qosymsha=qosymsha,
                            kutilgen=kutilgen_jup,
                            tuzetilgen=soz[: -len(qosymsha)] + kutilgen_jup,
                            songy_dauysty=songy,
                        )
                    )
                break
            else:
                continue
            break

    return tabylgan


if __name__ == "__main__":
    import sys

    mati = " ".join(sys.argv[1:]) or sys.stdin.read()
    tabylgan = tekseru(mati)
    if not tabylgan:
        print("Үндестік бұзылған сөз табылмады.")
    else:
        print(f"Үміткер: {len(tabylgan)}\n")
        for u in tabylgan:
            print(f"  {u}")
