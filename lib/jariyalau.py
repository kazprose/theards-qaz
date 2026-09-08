"""Жариялау қабаты: қай жолмен постталатынын анықтайды.

Әдейі ЕШҚАНДАЙ нақты SaaS-қа байланбаған. Түпнұсқа `threads-skills` бандлы
Publora-ны әдепкі жол етіп қойған, ол ыңғайлы, бірақ бір компанияға тәуелділік
тудырады. Мұнда әдепкі — қолмен қою, ал автопост қалайтын адам өз командасын
қосады.

Екі деңгей:

  0-деңгей — QOLDAN (әдепкі, ешқандай баптау керек емес)
      Драфт көшіріп-қоюға дайын блок болып қайтады. Кілт те, тіркелу де
      керек емес.

  1-деңгей — OZINDIK (қаласаң)
      `THREADS_POSTER` айнымалысына өз командаңды жазасың. Шеберлік
      мақұлданғаннан кейін сол команданы шақырып, драфтты stdin арқылы
      JSON пішімінде береді:

          {"turi": "post", "mati": "...", "nysana_url": null}

      Команда 0 қайтарса — сәтті. Ол команданы Publora API-ымен де,
      Threads Graph API-ымен де, кез келген басқа жолмен де жаза аласың.
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
from typing import Any, Literal, Optional

Qabat = Literal["qoldan", "ozindik"]
Turi = Literal["post", "tred", "jauap", "dayekshe"]

# Басқа адамның постына жауап пен дәйексөз посты — бөлек пост. Оны автоматты
# жариялау қате нысанаға түсу қаупін тудырады, сондықтан әрқашан қолмен.
QOLDAN_GANA: frozenset[str] = frozenset({"jauap", "dayekshe"})


def qabat() -> Qabat:
    """Белсенді жариялау қабатын қайтарады."""
    return "ozindik" if os.getenv("THREADS_POSTER") else "qoldan"


def qoldan_habar(mati: str, nysana_url: str, turi: str = "post") -> str:
    """Қолмен қою нұсқауын құрастырады."""
    qayda = {
        "post": "Threads-те жаңа пост ретінде қой",
        "tred": "Threads композерінде қой (әр блок — бір пост)",
        "jauap": "төмендегі постқа жауап ретінде қой",
        "dayekshe": "төмендегі постты дәйексөзге алып, осы мәтінді қос",
    }.get(turi, "Threads-те қой")

    return f"""Драфт мақұлданды. Мәтінді көшіріп, {qayda}:

```
{mati}
```

**Сілтеме:** {nysana_url}

---

Автопост қалайсың ба? `THREADS_POSTER` айнымалысына өз командаңды жаз —
драфт stdin арқылы JSON болып беріледі. Нұсқау: `.env.example`.
"""


def jariyala(
    turi: Turi,
    mati: str,
    nysana_url: str = "https://www.threads.com/",
    **qosymsha: Any,
) -> dict[str, Any]:
    """Мақұлданған драфтты белсенді қабатқа жібереді.

    Жауап пен дәйексөз әрқашан қолмен қайтады: олар басқа адамның постына
    байланатын бөлек пост, ал автопост оны қате нысанаға жіберуі мүмкін.

    Returns:
        qoldan:  {"qabat": "qoldan", "habar": <көшіріп-қою блогы>}
        ozindik: {"qabat": "ozindik", "kod": int, "stdout": str, "stderr": str}
    """
    belsendi = qabat()

    if turi in QOLDAN_GANA or belsendi == "qoldan":
        return {
            "qabat": "qoldan",
            "habar": qoldan_habar(mati, nysana_url, turi),
        }

    komanda = os.environ["THREADS_POSTER"]
    juk = json.dumps(
        {"turi": turi, "mati": mati, "nysana_url": nysana_url, **qosymsha},
        ensure_ascii=False,
    )
    natije = subprocess.run(
        shlex.split(komanda),
        input=juk,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {
        "qabat": "ozindik",
        "kod": natije.returncode,
        "stdout": natije.stdout,
        "stderr": natije.stderr,
    }
