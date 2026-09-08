"""Жариялау алдындағы толық тексеру: емле + тіл тазалығы бір есепте.

`threads-redaktor` шеберлігі `--mode audit` режимінде осыны шақырады.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import emle as _emle
from . import kalka as _kalka
from . import undestik as _undestik


@dataclass
class ToliqEsep:
    emle: _emle.EmleEsebi
    kalka: _kalka.KalkaEsebi
    undestik: list[_undestik.Undestik]

    @property
    def joneltuge_dayin(self) -> bool:
        """Қатты қате жоқ па (гомоглиф, көлем, хэштег)?"""
        return self.emle.taza

    def __str__(self) -> str:
        bas = "# Жариялау алдындағы тексеру\n"
        qorytyndy = (
            "✅ Қатты қате жоқ, жіберуге болады."
            if self.joneltuge_dayin
            else "⛔ Түзетілмеген қате бар, жіберме."
        )
        und = (
            "\n".join(f"  {u}" for u in self.undestik)
            if self.undestik
            else "Үндестік бұзылған сөз табылмады."
        )
        return (
            f"{bas}\n## 1. Емле мен шектеулер\n\n{self.emle}\n\n"
            f"## 2. Тіл тазалығы\n\n{self.kalka}\n\n"
            f"## 3. Дауысты үндестігі\n\n{und}\n\n"
            f"## Қорытынды\n\n{qorytyndy}"
        )


def tolyq(mati: str, uzin_forma: bool = False) -> ToliqEsep:
    """Мәтінді екі модульмен де тексеріп, бір есеп қайтарады."""
    return ToliqEsep(
        emle=_emle.tekseru(mati, uzin_forma=uzin_forma),
        kalka=_kalka.tekseru(mati),
        undestik=_undestik.tekseru(mati),
    )


if __name__ == "__main__":
    import sys

    mati = " ".join(sys.argv[1:]) or sys.stdin.read()
    esep = tolyq(mati)
    print(esep)
    raise SystemExit(0 if esep.joneltuge_dayin else 1)
