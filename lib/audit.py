"""Жариялау алдындағы толық тексеру бір есепте.

Төрт қабат:
    1. Емле мен Threads шектеулері  (lib/emle.py)
    2. Тіл тазалығы                  (lib/kalka.py)
    3. Дауысты үндестігі             (lib/undestik.py)
    4. Дауыс профиліне сәйкестік     (lib/profil.py) — профиль болса ғана

`threads-redaktor` шеберлігі `--mode audit` режимінде осыны шақырады.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

from . import emle as _emle
from . import kalka as _kalka
from . import profil as _profil
from . import undestik as _undestik

# Шақырушы профильді бермесе, дискіден өзі оқиды. `profil=None` деп ашық
# берсе — профильсіз тексереді. Екеуін ажырату үшін жеке белгі керек.
AVTO = object()


@dataclass
class ToliqEsep:
    emle: _emle.EmleEsebi
    kalka: _kalka.KalkaEsebi
    undestik: list[_undestik.Undestik]
    profil: list[_emle.Belgi] = field(default_factory=list)
    profil_bar: bool = False

    @property
    def qateler(self) -> list[_emle.Belgi]:
        """Түзетілмей жіберуге болмайтын белгілер."""
        return self.emle.qateler + [b for b in self.profil if b.dengei == "qate"]

    @property
    def joneltuge_dayin(self) -> bool:
        return not self.qateler

    def __str__(self) -> str:
        und = (
            "\n".join(f"  {u}" for u in self.undestik)
            if self.undestik
            else "Үндестік бұзылған сөз табылмады."
        )
        # Табылған белгі профиль бар-жоғына қарамай әрқашан көрсетіледі:
        # регистрдің араласуы профильсіз де қате.
        jol = [f"  {b}" for b in self.profil]
        if not self.profil_bar:
            if not jol:
                jol.append("Профильге қатысты белгі жоқ.")
            jol += [
                "",
                "Дауыс профилі толтырылмаған, сондықтан профильге сай регистр",
                "мен тыйым салынған сөздер тексерілмеді. Жасау:",
                "  python3 -m lib.profil ulgi > .threads-profil.md",
            ]
        elif not jol:
            jol.append("Профильге сай.")
        prof = "\n".join(jol)

        qorytyndy = (
            "✅ Қатты қате жоқ, жіберуге болады."
            if self.joneltuge_dayin
            else "⛔ Түзетілмеген қате бар, жіберме."
        )
        return (
            f"# Жариялау алдындағы тексеру\n\n"
            f"## 1. Емле мен шектеулер\n\n{self.emle}\n\n"
            f"## 2. Тіл тазалығы\n\n{self.kalka}\n\n"
            f"## 3. Дауысты үндестігі\n\n{und}\n\n"
            f"## 4. Дауыс профилі\n\n{prof}\n\n"
            f"## Қорытынды\n\n{qorytyndy}"
        )


def tolyq(
    mati: str,
    uzin_forma: bool = False,
    profil: Union[Optional[_profil.Profil], object] = AVTO,
    profil_joly: Optional[Path] = None,
) -> ToliqEsep:
    """Мәтінді төрт қабатпен тексеріп, бір есеп қайтарады.

    Args:
        mati: Тексерілетін пост немесе тред блогы.
        uzin_forma: Мәтін тіркемесі бар ұзын пост (10 000 таңба) болса True.
        profil: Дауыс профилі. Әдепкі күйде дискіден өзі оқылады.
            `None` берсең — профильсіз тексеріледі (регистрдің араласуы
            бәрібір ұсталады).
        profil_joly: Профиль файлының жолы, әдепкіден басқа болса.
    """
    p = _profil.oqy(profil_joly) if profil is AVTO else profil
    if not isinstance(p, _profil.Profil):
        p = None

    return ToliqEsep(
        emle=_emle.tekseru(mati, uzin_forma=uzin_forma),
        kalka=_kalka.tekseru(mati),
        undestik=_undestik.tekseru(mati),
        profil=_profil.saikestik(mati, p),
        profil_bar=p is not None,
    )


if __name__ == "__main__":
    import sys

    mati = " ".join(sys.argv[1:]) or sys.stdin.read()
    esep = tolyq(mati)
    print(esep)
    raise SystemExit(0 if esep.joneltuge_dayin else 1)
