"""Пост журналы: не жарияланды, не болды.

Бандлдағы ең үлкен олқылықты жабады. Шеберліктер пост жазады да, тоқтайды —
нәтижесін ешкім жазып алмайды. Сондықтан `references/hook-formulasy.md`
ішіндегі формулалар мәңгі БОЛЖАМ күйінде қалады.

Бұл модуль сол шеңберді жабады: әр постты формуласымен бірге жазып қоясың,
кейін Threads Insights-тен алған нақты сандарды қосасың. Бірнеше аптадан
кейін `qorytu()` СЕНІҢ аудиторияңда қай формула жүретінін көрсетеді.

Дерек қайдан келеді: Threads Insights экранынан, ҚОЛМЕН. Бандл ешқандай
санды өзі тартпайды әрі ойлап шығармайды. Сан жоқ болса — жоқ, болжам
жазылмайды.

Файл пішімі — JSONL (әр жол бір пост), әдепкі орны `.threads-jurnal.jsonl`.
Қарапайым: мәтіндік редактормен де ашып түзетуге болады, git-ке де сыяды.
"""
from __future__ import annotations

import json
import os
import statistics
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Optional

ADEPKI_JOL = Path(os.getenv("THREADS_JURNAL", ".threads-jurnal.jsonl"))

# Осы саннан аз пост болса, қорытынды жасамаймыз. Шағын аудиторияда
# бір вирусты пост бүкіл орташаны бұзады.
EN_AZ_ULGI = 5

MAQSATTAR = ("jauap", "repost", "laik", "dayekshe")


@dataclass
class Olshem:
    """Threads Insights-тен қолмен көшірілген сандар.

    Бәрі міндетті емес: білгеніңді жаз, қалғанын `None` қалдыр.
    `korsetilim` — «Views»/«Көрсетілім».
    """

    korsetilim: Optional[int] = None
    jauap: Optional[int] = None
    repost: Optional[int] = None
    laik: Optional[int] = None
    dayekshe: Optional[int] = None

    @property
    def toly(self) -> bool:
        return self.korsetilim is not None and self.korsetilim > 0

    @property
    def barlyq_areket(self) -> Optional[int]:
        bolshek = [self.jauap, self.repost, self.laik, self.dayekshe]
        bar = [x for x in bolshek if x is not None]
        return sum(bar) if bar else None

    def areket_ulesi(self) -> Optional[float]:
        """Барлық әрекеттің көрсетілімге қатынасы."""
        areket = self.barlyq_areket
        if not self.toly or areket is None:
            return None
        return areket / self.korsetilim

    def jauap_ulesi(self) -> Optional[float]:
        """Жауаптың көрсетілімге қатынасы — Threads-тегі ең ауыр сигнал."""
        if not self.toly or self.jauap is None:
            return None
        return self.jauap / self.korsetilim


@dataclass
class Jazba:
    """Журналдағы бір пост."""

    kuni: str
    formula: str                  # «Q3» немесе «—» (формуласыз)
    maqsat: str                   # jauap | repost | laik | dayekshe
    turi: str = "post"            # post | tred
    tanba: Optional[int] = None
    mati_bas: str = ""            # алғашқы 80 таңба, тану үшін
    url: str = ""
    eskertpe: str = ""
    olshem: Olshem = field(default_factory=Olshem)

    def json_qatar(self) -> str:
        d = asdict(self)
        d["olshem"] = {k: v for k, v in d["olshem"].items() if v is not None}
        return json.dumps(d, ensure_ascii=False)


def _jol(jol: Optional[Path] = None) -> Path:
    return Path(jol) if jol else ADEPKI_JOL


def jaz(jazba: Jazba, jol: Optional[Path] = None) -> Path:
    """Журналға бір жазба қосады."""
    p = _jol(jol)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(jazba.json_qatar() + "\n")
    return p


def oqy(jol: Optional[Path] = None) -> list[Jazba]:
    """Журналды оқиды. Файл жоқ болса — бос тізім."""
    p = _jol(jol)
    if not p.exists():
        return []
    jazbalar: list[Jazba] = []
    for qatar in p.read_text(encoding="utf-8").splitlines():
        qatar = qatar.strip()
        if not qatar:
            continue
        d: dict[str, Any] = json.loads(qatar)
        d["olshem"] = Olshem(**d.get("olshem", {}))
        jazbalar.append(Jazba(**d))
    return jazbalar


@dataclass
class FormulaQorytyndy:
    formula: str
    sany: int
    olshengen: int                        # саны бар посттар
    ortasha_areket: Optional[float]       # медиана
    ortasha_jauap: Optional[float]        # медиана
    senimdi: bool                         # үлгі жеткілікті ме

    def __str__(self) -> str:
        if self.olshengen == 0:
            return f"{self.formula}: {self.sany} пост, саны жазылмаған"
        a = f"{self.ortasha_areket:.2%}" if self.ortasha_areket is not None else "—"
        j = f"{self.ortasha_jauap:.2%}" if self.ortasha_jauap is not None else "—"
        belgi = "" if self.senimdi else "  ⚠ үлгі аз"
        return (
            f"{self.formula}: {self.olshengen}/{self.sany} өлшенген | "
            f"әрекет {a} | жауап {j}{belgi}"
        )


def _mediana(mander: Iterable[Optional[float]]) -> Optional[float]:
    bar = [m for m in mander if m is not None]
    return statistics.median(bar) if bar else None


def qorytu(
    jazbalar: Optional[list[Jazba]] = None, jol: Optional[Path] = None
) -> list[FormulaQorytyndy]:
    """Формула бойынша қорытады.

    Орташа емес, МЕДИАНА қолданылады: бір вирусты пост орташаны бұрмалайды,
    ал шағын аудиторияда ондай пост жиі кездеседі.
    """
    jazbalar = oqy(jol) if jazbalar is None else jazbalar

    toptar: dict[str, list[Jazba]] = {}
    for j in jazbalar:
        toptar.setdefault(j.formula, []).append(j)

    natije = [
        FormulaQorytyndy(
            formula=formula,
            sany=len(top),
            olshengen=sum(1 for j in top if j.olshem.toly),
            ortasha_areket=_mediana(j.olshem.areket_ulesi() for j in top),
            ortasha_jauap=_mediana(j.olshem.jauap_ulesi() for j in top),
            senimdi=sum(1 for j in top if j.olshem.toly) >= EN_AZ_ULGI,
        )
        for formula, top in toptar.items()
    ]
    natije.sort(key=lambda q: (q.ortasha_jauap is None, -(q.ortasha_jauap or 0)))
    return natije


def esep(jol: Optional[Path] = None) -> str:
    """Оқуға ыңғайлы қорытынды есеп."""
    jazbalar = oqy(jol)
    if not jazbalar:
        return (
            "Журнал бос. Бірінші постты жазып қой:\n"
            "  python3 -m lib.jurnal qos Q3 jauap 'постың басы'\n"
        )

    olshengen = sum(1 for j in jazbalar if j.olshem.toly)
    jol_tizim = [
        f"Барлығы: {len(jazbalar)} пост, оның {olshengen}-ы өлшенген.",
        "",
        "## Формула бойынша (жауап үлесі бойынша реттелген)",
        "",
    ]
    jol_tizim += [f"  {q}" for q in qorytu(jazbalar)]

    if olshengen < EN_AZ_ULGI:
        jol_tizim += [
            "",
            f"⚠ Өлшенген пост {EN_AZ_ULGI}-тен аз. Бұл сандардан ҚОРЫТЫНДЫ",
            "  ЖАСАУҒА БОЛМАЙДЫ — әзірге бұл жай ғана журнал.",
        ]
    else:
        jol_tizim += [
            "",
            "Ескерту: бұл — сенің аудиторияңдағы бақылау, жалпы заңдылық емес.",
            "Формуланы ауыстырғанда тақырып та өзгереді, сондықтан айырманы",
            "тек формулаға телуге болмайды. Күмәнді жерді қайталап тексер.",
        ]
    return "\n".join(jol_tizim)


def _cli(argv: list[str]) -> int:
    if not argv or argv[0] in ("esep", "-h", "--help"):
        print(esep())
        return 0

    if argv[0] == "qos" and len(argv) >= 4:
        jaz(
            Jazba(
                kuni=date.today().isoformat(),
                formula=argv[1],
                maqsat=argv[2],
                mati_bas=argv[3][:80],
            )
        )
        print(f"Жазылды: {argv[1]} / {argv[2]}. Сандарын кейін қосасың.")
        return 0

    print(
        "Қолданысы:\n"
        "  python3 -m lib.jurnal esep\n"
        "  python3 -m lib.jurnal qos <формула> <мақсат> <мәтіннің басы>\n\n"
        "Сандарды қосу үшін .threads-jurnal.jsonl файлын тікелей түзет:\n"
        '  "olshem": {"korsetilim": 1200, "jauap": 14, "repost": 3, "laik": 40}',
    )
    return 1


if __name__ == "__main__":
    import sys

    raise SystemExit(_cli(sys.argv[1:]))
