"""Жариялау қабаты: қай жолмен постталатынын анықтайды.

Әдейі ЕШҚАНДАЙ нақты SaaS-қа байланбаған. Түпнұсқа `threads-skills` бандлы
Publora-ны әдепкі жол етіп қойған, ол ыңғайлы, бірақ бір компанияға тәуелділік
тудырады. Мұнда әдепкі — қолмен қою, ал автопост қалайтын адам өз командасын
қосады.

Екі деңгей:

  0-деңгей — QOLDAN (әдепкі, ешқандай баптау керек емес)
      Драфт көшіріп-қоюға дайын блок болып қайтады. Кілт те, тіркелу де
      керек емес.

  1-деңгей — THREADS (ресми API)
      `THREADS_TOKEN` бар болса, пост Threads-тің өз API-ы арқылы
      жарияланады. Баптауы: `lib/threads_api.py` құжаттамасын қара.

  2-деңгей — OZINDIK (қаласаң)
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

Qabat = Literal["qoldan", "threads", "ozindik"]
Turi = Literal["post", "tred", "jauap", "dayekshe"]

# Басқа адамның постына жауап пен дәйексөз посты — бөлек пост. Оны автоматты
# жариялау қате нысанаға түсу қаупін тудырады, сондықтан әрқашан қолмен.
QOLDAN_GANA: frozenset[str] = frozenset({"jauap", "dayekshe"})


def qabat() -> Qabat:
    """Белсенді жариялау қабатын қайтарады.

    Реті: ресми API → өз командаң → қолмен.
    """
    from .threads_api import token_oqy

    try:
        if token_oqy():
            return "threads"
    except Exception:
        pass  # токен файлы бұзық болса, төменгі қабатқа түсеміз
    return "ozindik" if os.getenv("THREADS_POSTER") else "qoldan"


def avto_rejim() -> bool:
    """Мақұлдаусыз жариялау қосылған ба.

    Екі шарт бірге керек: `THREADS_AVTO` қойылған ЖӘНЕ жариялайтын қабат
    бар. Қолмен қою қабатында автоматтандыратын ештеңе жоқ.
    """
    return bool(os.getenv("THREADS_AVTO")) and qabat() != "qoldan"


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
        threads: {"qabat": "threads", "satti": bool, "post_id"|"qate": str}
        ozindik: {"qabat": "ozindik", "kod": int, "stdout": str, "stderr": str}
    """
    belsendi = qabat()

    if turi in QOLDAN_GANA or belsendi == "qoldan":
        return {
            "qabat": "qoldan",
            "habar": qoldan_habar(mati, nysana_url, turi),
        }

    if belsendi == "threads":
        from .threads_api import ThreadsApi, ThreadsQate

        try:
            post_id = ThreadsApi().jaria(mati)
        except ThreadsQate as e:
            return {"qabat": "threads", "satti": False, "qate": str(e)}
        return {"qabat": "threads", "satti": True, "post_id": post_id}

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


def avto_jariyala(
    turi: Turi,
    mati: str,
    esep: Any,
    nysana_url: str = "https://www.threads.com/",
    **qosymsha: Any,
) -> dict[str, Any]:
    """Мақұлдаусыз жариялайды — БІРАҚ тек тексеруден өткен драфтты.

    Автоматтандырудың мәні әр посттың басында отырмау. Ал бұзық посттың
    автоматты шығуы — автоматтандырудың мәнін жоққа шығарады. Сондықтан
    қақпа алынбайды, ол САПАҒА байланады:

        тексеру таза  → жарияланады
        бір қате бар  → тоқтайды, себебін айтады

    Жауап пен дәйексөз бұл жерде де автоматты жарияланбайды: олар бөтен
    постқа байланатын бөлек пост, қате нысанаға түсу қаупі бар.

    Args:
        esep: `lib.audit.tolyq()` қайтарған есеп. `joneltuge_dayin`
            өрісі бар кез келген нысан жарайды.

    Returns:
        Жарияланса — `jariyala()` нәтижесі, `avto: True` қосылған.
        Тоқтаса — {"avto": False, "sebep": ...} және мақұлдауға арналған
        қолмен қою блогы.
    """
    def _toqta(sebep: str) -> dict[str, Any]:
        """Автоматты жарияламай, адамға көрсетеді.

        МАҢЫЗДЫ: мұнда `jariyala()` шақырылмайды. Ол шақырылса, драфт
        белсенді қабат арқылы БӘРІБІР жарияланып кетер еді де,
        тексеру қақпасының мәні жойылар еді.
        """
        return {
            "avto": False,
            "sebep": sebep,
            "qabat": "qoldan",
            "habar": qoldan_habar(mati, nysana_url, turi),
        }

    if not avto_rejim():
        return _toqta(
            "Автоматты режим қосылмаған. Қосу: THREADS_AVTO=1 "
            "(әрі жариялайтын қабат бапталуы керек)."
        )

    if turi in QOLDAN_GANA:
        return _toqta(
            "Жауап пен дәйексөз автоматты жарияланбайды: олар бөтен постқа "
            "байланады, ал қате нысанаға түсу қаупі бар."
        )

    if not getattr(esep, "joneltuge_dayin", False):
        tizim = "; ".join(b.habar for b in (getattr(esep, "qateler", None) or []))
        return _toqta(f"Тексеруден өтпеді, сондықтан жарияланбады. {tizim}")

    return {"avto": True, **jariyala(turi, mati, nysana_url, **qosymsha)}
