"""Дауыс профилі: сен кімсің, аудиторияң кім, қалай сөйлейсің.

Мәселе: әр шеберлік аудиторияны, регистрді, тақырыпты қайта-қайта сұрайды.
Пайдаланушы оны бес рет жазады, ал алтыншысында басқаша жазады да, посттар
бір-біріне ұқсамай қалады.

Шешім: бір рет толтырылатын профиль. Қалған шеберліктер соны оқиды.

Файл — `.threads-profil.md`, қарапайым markdown. Адам да оқи алады, редактормен
де түзетеді, git-ке де сыяды. Пішімі қатаң емес: тек `## ` тақырыптары
танылады, ішіндегі мәтін еркін.

Ең құндысы — профильдің ТЕКСЕРІЛЕТІН бөлігі. «Сен» деп жазатыныңды айтсаң,
`saikestik()` драфтта «сіз» шығып кеткенін ұстайды. Бұл — бандлдағы жалғыз
жер, онда профиль жай нұсқаулық емес, нақты ереже болып істейді.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .emle import Belgi, _kontekst

ADEPKI_JOL = Path(os.getenv("THREADS_PROFIL", ".threads-profil.md"))

BOLIMDER = ("Кім", "Аудитория", "Регистр", "Бағаналар", "Айтпайтын сөздер", "Мысалдар")

# --- Регистр белгілері ------------------------------------------------------
# Тек СЕНІМДІ белгілер алынған. Күмәнділері әдейі қалдырылмаған:
# «-сыз/-сіз» етістік жалғауы да, «-сыз» болымсыздық жұрнағы да бола алады
# («келесіз» — сіз, ал «мәнсіз» — жұрнақ), сондықтан ол тексерілмейді.
# Азырақ ұстау — жалған белгі беруден жақсы.

SIZ_ULGILER = [
    re.compile(r"\bсіз(?:ге|ді|дің|бен|де|ден|дер\w*)?\b", re.IGNORECASE),
    re.compile(r"\b\w+(?:ңыз|ңіз)\b", re.IGNORECASE),        # қараңыз, атыңыз
    re.compile(r"\b\w+(?:сыздар|сіздер)\b", re.IGNORECASE),  # келесіздер
]

# «сен» — тек нақты сөз тізімі. `сен\w*` деп алуға БОЛМАЙДЫ: «сенім»,
# «сенбі», «сенімді» деген мүлдем бөлек сөздер бар.
SEN_SOZDER = {
    "сен", "сені", "сенің", "саған", "сенде", "сенен", "сенімен", "сендер",
    "сендерге", "сендерді", "сендердің",
}
SEN_ULGILER = [
    re.compile(r"\b\w+(?:сың|сің)\b", re.IGNORECASE),  # келесің, білесің
]

SOZ = re.compile(r"[\wЀ-ӿ]+", re.UNICODE)


@dataclass
class Profil:
    """Толтырылған дауыс профилі."""

    kim: str = ""
    audytoriya: str = ""
    registr: str = ""              # «сен» | «сіз» | «»
    kod_auystyru: str = ""         # «еркін» | «шамалы» | «таза қазақша» | «»
    baganalar: list[str] = field(default_factory=list)
    aitpaityn_sozder: list[str] = field(default_factory=list)
    mysaldar: str = ""
    shikizat: dict[str, str] = field(default_factory=dict)

    @property
    def toly(self) -> bool:
        """Профиль пайдалы болу үшін ең азы толтырылған ба."""
        return bool(self.kim and self.audytoriya and self.registr)

    @property
    def bos_orindar(self) -> list[str]:
        bos = []
        if not self.kim:
            bos.append("Кім")
        if not self.audytoriya:
            bos.append("Аудитория")
        if not self.registr:
            bos.append("Регистр (сен/сіз)")
        if not self.baganalar:
            bos.append("Бағаналар")
        return bos

    def qysqasha(self) -> str:
        jol = [f"Кім: {self.kim or '—'}", f"Аудитория: {self.audytoriya or '—'}"]
        jol.append(f"Регистр: {self.registr or '—'}"
                   + (f", кодты ауыстыру: {self.kod_auystyru}" if self.kod_auystyru else ""))
        if self.baganalar:
            jol.append("Бағаналар: " + ", ".join(self.baganalar))
        if self.aitpaityn_sozder:
            jol.append("Айтпайтын сөздер: " + ", ".join(self.aitpaityn_sozder))
        return "\n".join(jol)


def _bolimder(mati: str) -> dict[str, str]:
    """Markdown-ды `## ` тақырыптары бойынша бөлікке жарады."""
    bolimder: dict[str, str] = {}
    agymdagy: Optional[str] = None
    jinalgan: list[str] = []
    for qatar in mati.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", qatar)
        if m:
            if agymdagy:
                bolimder[agymdagy] = "\n".join(jinalgan).strip()
            agymdagy, jinalgan = m.group(1), []
        elif agymdagy:
            jinalgan.append(qatar)
    if agymdagy:
        bolimder[agymdagy] = "\n".join(jinalgan).strip()
    return bolimder


def _tizim(mati: str) -> list[str]:
    """`- ` тармақтарын тізімге жинайды, түсініктеме жолдарын алып тастайды."""
    tarmaqtar = []
    for qatar in mati.splitlines():
        m = re.match(r"^\s*[-*]\s+(.+?)\s*$", qatar)
        if m and not m.group(1).startswith("<!--"):
            tarmaqtar.append(m.group(1))
    return tarmaqtar


def _mander(mati: str) -> dict[str, str]:
    """`- Кілт: мән` жолдарын сөздікке жинайды."""
    return {
        m.group(1).strip().lower(): m.group(2).strip()
        for qatar in mati.splitlines()
        if (m := re.match(r"^\s*[-*]\s+([^:]+):\s*(.+?)\s*$", qatar))
    }


def _tazala(man: str) -> str:
    """Толтырылмаған үлгі мәнін бос деп санайды."""
    man = man.strip().strip("«»\"'").strip()
    bos_belgi = ("...", "…", "—", "-", "мұнда", "толтыр")
    return "" if not man or man.lower().startswith(bos_belgi) else man


def oqy(jol: Optional[Path] = None) -> Optional[Profil]:
    """Профильді оқиды. Файл жоқ болса — None."""
    p = Path(jol) if jol else ADEPKI_JOL
    if not p.exists():
        return None

    bolimder = _bolimder(p.read_text(encoding="utf-8"))
    registr_mander = _mander(bolimder.get("Регистр", ""))

    registr = _tazala(registr_mander.get("сен/сіз", "")).lower()
    registr = registr if registr in ("сен", "сіз") else ""

    return Profil(
        kim=_tazala(bolimder.get("Кім", "").split("\n")[0]),
        audytoriya=_tazala(bolimder.get("Аудитория", "").split("\n")[0]),
        registr=registr,
        kod_auystyru=_tazala(registr_mander.get("кодты ауыстыру", "")).lower(),
        baganalar=[_tazala(t) for t in _tizim(bolimder.get("Бағаналар", "")) if _tazala(t)],
        aitpaityn_sozder=[
            _tazala(t) for t in _tizim(bolimder.get("Айтпайтын сөздер", "")) if _tazala(t)
        ],
        mysaldar=bolimder.get("Мысалдар", ""),
        shikizat=bolimder,
    )


# --- Регистрді тексеру ------------------------------------------------------

def registr_tabu(mati: str) -> tuple[int, int]:
    """Мәтіндегі «сен» мен «сіз» белгілерін санайды.

    Returns:
        (сен белгісінің саны, сіз белгісінің саны)
    """
    sen = sum(1 for s in SOZ.findall(mati) if s.lower() in SEN_SOZDER)
    sen += sum(len(u.findall(mati)) for u in SEN_ULGILER)
    siz = sum(len(u.findall(mati)) for u in SIZ_ULGILER)
    return sen, siz


def saikestik(mati: str, profil: Optional[Profil] = None) -> list[Belgi]:
    """Драфтты профильге қарсы тексереді.

    Профиль берілмесе де бір нәрсе тексеріледі: бір постта «сен» мен «сіз»
    араласса, ол профильге тәуелсіз қате.
    """
    belgiler: list[Belgi] = []
    sen, siz = registr_tabu(mati)

    if sen and siz:
        belgiler.append(
            Belgi(
                turi="регистр",
                dengei="qate",
                habar=(
                    f"Бір постта «сен» де ({sen} белгі), «сіз» де ({siz} белгі) "
                    "қолданылған. Біреуін таңда — регистрдің ортасында ауысуы "
                    "ең байқалатын жасандылық."
                ),
            )
        )
    elif profil and profil.registr:
        kutilgen = profil.registr
        naqty = "сен" if sen and not siz else "сіз" if siz and not sen else ""
        if naqty and naqty != kutilgen:
            belgiler.append(
                Belgi(
                    turi="регистр",
                    dengei="eskertu",
                    habar=(
                        f"Профильде «{kutilgen}» деп жазылған, ал драфтта "
                        f"«{naqty}» қолданылған. Профильді өзгерттің бе, әлде "
                        "бұл байқаусыз ба?"
                    ),
                )
            )

    if profil:
        for soz in profil.aitpaityn_sozder:
            taza = soz.strip()
            if not taza:
                continue
            ulgi = re.compile(rf"\b{re.escape(taza)}", re.IGNORECASE)
            if (m := ulgi.search(mati)):
                belgiler.append(
                    Belgi(
                        turi="тыйым",
                        dengei="eskertu",
                        habar=(
                            f"«{taza}» — профильдегі айтпайтын сөздер тізімінде. "
                            "Басқаша айт."
                        ),
                        uzindi=_kontekst(mati, m.start()),
                    )
                )
    return belgiler


def ulgi() -> str:
    """Толтыруға дайын профиль үлгісін қайтарады."""
    return """# Дауыс профилі

<!-- Бір рет толтырасың, бандлдағы барлық шеберлік осыны оқиды.
     Толтырылмаған бөлім жай ғана ескерілмейді, қате шықпайды. -->

## Кім

<!-- Бір сөйлем: не істейсің. Нақты болсын.
     ❌ «технологиялық жоба»
     ✅ «қазақша оқу қосымшасын жасаймын, өзім бір адаммын» -->

...

## Аудитория

<!-- Кім оқиды. «Бәрі» деп жазсаң, посттар да жалпылама шығады.
     ✅ «мектеп мұғалімдері мен бастауыш сынып ата-аналары» -->

...

## Регистр

<!-- Мұны толтыру ЕҢ маңызды: бандл осыны машинамен тексереді. -->

- Сен/сіз: ...
- Кодты ауыстыру: ...

<!-- Сен/сіз: «сен» (Threads-те табиғи) немесе «сіз» (ресми бренд аккаунты).
     Кодты ауыстыру:
       еркін       — «дедлайнға үлгермедік», IT/стартап ортасы
       шамалы      — қажет терминді ғана қалдырасың
       таза қазақша — терминді де қазақшалайсың -->

## Бағаналар

<!-- 3-4 тұрақты тақырып. Әрқайсысы бір рөл атқарады.
     references/hook-formulasy.md ішіндегі формулалармен байланысады. -->

- ...
- ...
- ...

## Айтпайтын сөздер

<!-- Сенің брендіңе жат сөздер. Бандл драфтта кездессе ескертеді.
     Мысалы: «үздік», «инновациялық», «синергия», бәсекелестің аты. -->

- ...

## Мысалдар

<!-- Өзің жазған, дауысыңды дәл көрсететін 2-3 пост. Еркін мәтін.
     Бұл — ең пайдалы бөлім: ережеден гөрі мысал көбірек үйретеді. -->

...
"""


def jaz(mazmun: str, jol: Optional[Path] = None) -> Path:
    """Профильді файлға жазады."""
    p = Path(jol) if jol else ADEPKI_JOL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(mazmun, encoding="utf-8")
    return p


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "ulgi":
        print(ulgi())
    elif (p := oqy()) is None:
        print(
            f"Профиль жоқ ({ADEPKI_JOL}).\n\n"
            "Үлгіні жасау:\n"
            f"  python3 -m lib.profil ulgi > {ADEPKI_JOL}"
        )
        raise SystemExit(1)
    else:
        print(p.qysqasha())
        if p.bos_orindar:
            print("\nТолтырылмаған: " + ", ".join(p.bos_orindar))
