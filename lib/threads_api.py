"""Threads-тің ресми Graph API клиенті.

Не үшін: журналға сандарды қолмен теру — оның өлетін жері. Екі апта
тересің, үшіншісінде тастайсың. Бұл модуль соны автоматтандырады.

Не істейді:
    * өз посттарыңның тізімін алады
    * әр посттың статистикасын тартады (көрсетілім, жауап, репост, лайк, дәйексөз)
    * жаңа пост жариялайды (екі қадамды: контейнер → жариялау)

Не істемейді:
    * бөтен аккаунттың дерегін алмайды — API оны бермейді
    * скрапинг жасамайды

Тәуелділік жоқ: `urllib` стандартты кітапханадан.

Токен қайдан алынады
--------------------
1. https://developers.facebook.com — қосымша тіркеу, Threads API қосу
2. `threads_basic` және `threads_manage_insights` рұқсаттары
   (жариялау үшін `threads_content_publish` да керек)
3. Ұзақ мерзімді токен алу
4. Сақтау: `THREADS_TOKEN` айнымалысы немесе `.threads-token.json`

ЕСКЕРТУ: төмендегі код нақты API-мен сыналмаған — бұл ортада токен жоқ.
Сұрау құру, жауапты талдау, қате өңдеу сыналған (фикстуралармен). Ал тірі
шақыру алғаш іске қосқанда тексерілуі керек. Жауап пішімі күтілгеннен
басқаша болса, `_olshemdi_talda` функциясын түзетесің — ол екі белгілі
пішімді де қабылдайды.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

from .jurnal import Jazba, Olshem

BASE = "https://graph.threads.net/v1.0"
TOKEN_JOL = Path(os.getenv("THREADS_TOKEN_FILE", ".threads-token.json"))
KUTU = 30.0

# Insights сұрағанда қандай метрика керек.
METRIKALAR = ("views", "likes", "replies", "reposts", "quotes")

# API атауы → біздің `Olshem` өрісі.
OLSHEM_KARTA = {
    "views": "korsetilim",
    "replies": "jauap",
    "reposts": "repost",
    "likes": "laik",
    "quotes": "dayekshe",
}


class ThreadsQate(RuntimeError):
    """API қатесі немесе баптау қатесі."""


@dataclass
class Post:
    """API қайтарған бір пост."""

    id: str
    mati: str = ""
    kuni: str = ""
    url: str = ""


def token_oqy(jol: Optional[Path] = None) -> Optional[str]:
    """Токенді айнымалыдан не файлдан оқиды.

    Реті: `THREADS_TOKEN` айнымалысы → `.threads-token.json` файлы.
    Табылмаса — None.
    """
    if (t := os.getenv("THREADS_TOKEN")):
        return t.strip()
    p = Path(jol) if jol else TOKEN_JOL
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ThreadsQate(f"{p}: JSON оқылмады — {e}") from None
    t = d.get("token", "").strip()
    return t or None


def token_jaz(token: str, jol: Optional[Path] = None) -> Path:
    """Токенді файлға сақтайды.

    Файл `.gitignore` ішінде. Токен — құпия, репозиторийге түспеуі керек.
    """
    p = Path(jol) if jol else TOKEN_JOL
    p.write_text(json.dumps({"token": token}, ensure_ascii=False, indent=2) + "\n",
                 encoding="utf-8")
    try:
        p.chmod(0o600)
    except OSError:
        pass  # кейбір файлдық жүйеде жүрмейді, қатеге айналдырмаймыз
    return p


def _adepki_ashushy(url: str, derek: Optional[bytes], kutu: float) -> str:
    soraw = urllib.request.Request(url, data=derek, method="POST" if derek else "GET")
    if derek:
        soraw.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(soraw, timeout=kutu) as jauap:
        return jauap.read().decode("utf-8")


def _olshemdi_talda(derek: list[dict[str, Any]]) -> Olshem:
    """Insights жауабын `Olshem`-ге айналдырады.

    Threads екі пішімді де қайтара алады, сондықтан екеуі де оқылады:
        {"name": "views", "values": [{"value": 1234}]}
        {"name": "likes", "total_value": {"value": 42}}
    """
    mander: dict[str, int] = {}
    for jazba in derek:
        at = jazba.get("name")
        if at not in OLSHEM_KARTA:
            continue
        man: Any = None
        if isinstance(jazba.get("total_value"), dict):
            man = jazba["total_value"].get("value")
        elif isinstance(jazba.get("values"), list) and jazba["values"]:
            son = jazba["values"][-1]
            man = son.get("value") if isinstance(son, dict) else son
        if isinstance(man, (int, float)):
            mander[OLSHEM_KARTA[at]] = int(man)
    return Olshem(**mander)


class ThreadsApi:
    """Threads Graph API-дың жұқа клиенті."""

    def __init__(
        self,
        token: Optional[str] = None,
        *,
        ashushy: Optional[Callable[[str, Optional[bytes], float], str]] = None,
        kutu: float = KUTU,
    ):
        """
        Args:
            token: Кіру токені. Берілмесе — `token_oqy()` арқылы ізделеді.
            ashushy: HTTP шақыруын алмастыратын функция. Тестке керек;
                әдепкі күйде `urllib` қолданылады.
            kutu: Сұрауды күту уақыты, секунд.
        """
        self.token = token or token_oqy()
        if not self.token:
            raise ThreadsQate(
                "Threads токені жоқ. `THREADS_TOKEN` айнымалысын қой немесе\n"
                f"{TOKEN_JOL} файлын жаса. Нұсқау: skills/threads-natije/SKILL.md"
            )
        self._ashushy = ashushy or _adepki_ashushy
        self.kutu = kutu

    # --- ішкі ---------------------------------------------------------------

    def _shaqyr(self, jol: str, oristar: Optional[dict[str, str]] = None,
                *, post: bool = False) -> dict[str, Any]:
        oristar = {**(oristar or {}), "access_token": self.token}
        if post:
            url = f"{BASE}/{jol.lstrip('/')}"
            derek = urllib.parse.urlencode(oristar).encode()
        else:
            url = f"{BASE}/{jol.lstrip('/')}?{urllib.parse.urlencode(oristar)}"
            derek = None

        try:
            shikizat = self._ashushy(url, derek, self.kutu)
        except urllib.error.HTTPError as e:
            dene = e.read().decode("utf-8", errors="replace")
            raise ThreadsQate(self._qate_habary(e.code, dene)) from None
        except urllib.error.URLError as e:
            raise ThreadsQate(f"Желі қатесі: {e.reason}") from None

        try:
            jauap = json.loads(shikizat)
        except json.JSONDecodeError:
            raise ThreadsQate(f"API JSON емес жауап қайтарды: {shikizat[:200]}") from None

        if isinstance(jauap, dict) and "error" in jauap:
            qate = jauap["error"]
            raise ThreadsQate(
                f"API қатесі: {qate.get('message', qate)} "
                f"(код {qate.get('code')})"
            )
        return jauap

    @staticmethod
    def _qate_habary(kod: int, dene: str) -> str:
        habar = {
            190: None,  # төменде токен арқылы өңделеді
        }
        bas = {
            400: "Сұрау дұрыс емес",
            401: "Токен жарамсыз немесе мерзімі бітті — жаңасын ал",
            403: "Рұқсат жоқ. Қосымшада `threads_manage_insights` қосылған ба?",
            429: "Шектеуге жеттің — біраз күтіп қайта көр",
        }.get(kod, f"HTTP {kod}")
        try:
            qate = json.loads(dene).get("error", {})
            if (m := qate.get("message")):
                return f"{bas}: {m}"
        except (json.JSONDecodeError, AttributeError):
            pass
        return f"{bas}. Жауап: {dene[:200]}"

    # --- оқу ----------------------------------------------------------------

    def posttar(self, sany: int = 25) -> list[Post]:
        """Өз посттарыңның тізімін қайтарады, жаңасынан ескісіне қарай."""
        jauap = self._shaqyr(
            "me/threads",
            {"fields": "id,text,timestamp,permalink", "limit": str(max(1, sany))},
        )
        return [
            Post(
                id=str(p["id"]),
                mati=p.get("text", "") or "",
                kuni=(p.get("timestamp", "") or "")[:10],
                url=p.get("permalink", "") or "",
            )
            for p in jauap.get("data", [])
            if p.get("id")
        ]

    def olshem(self, post_id: str) -> Olshem:
        """Бір посттың статистикасын тартады."""
        jauap = self._shaqyr(
            f"{post_id}/insights", {"metric": ",".join(METRIKALAR)}
        )
        return _olshemdi_talda(jauap.get("data", []))

    # --- жазу ---------------------------------------------------------------

    def jaria(self, mati: str) -> str:
        """Мәтіндік пост жариялайды. Қайтаратыны — жаңа посттың id-і.

        Екі қадамды: алдымен контейнер жасалады, содан кейін жарияланады.
        Threads API солай құрылған.
        """
        konteiner = self._shaqyr(
            "me/threads", {"media_type": "TEXT", "text": mati}, post=True
        )
        if not (kid := konteiner.get("id")):
            raise ThreadsQate(f"Контейнер құрылмады: {konteiner}")

        natije = self._shaqyr("me/threads_publish", {"creation_id": str(kid)}, post=True)
        if not (pid := natije.get("id")):
            raise ThreadsQate(f"Жарияланбады: {natije}")
        return str(pid)


# --- Журналмен байланыс -----------------------------------------------------

def olshemderdi_janart(
    api: Optional[ThreadsApi] = None,
    jurnal_joly: Optional[Path] = None,
    sany: int = 25,
) -> tuple[int, int]:
    """Журналдағы өлшенбеген посттардың сандарын API-дан тартып толтырады.

    Журналдағы жазба API-дағы постпен `url` арқылы байланысады. Пост
    жарияланғанда `url` жазылмаса, оны байланыстыруға болмайды — сондықтан
    `threads-post-jazu` шеберлігі жариялағаннан кейін url-ды жазып қоюы керек.

    Returns:
        (жаңартылған жазба саны, байланыспаған жазба саны)
    """
    from . import jurnal as _jurnal

    api = api or ThreadsApi()
    p = Path(jurnal_joly) if jurnal_joly else _jurnal.ADEPKI_JOL
    jazbalar = _jurnal.oqy(p)
    if not jazbalar:
        return 0, 0

    # url → post_id
    karta = {post.url: post.id for post in api.posttar(sany) if post.url}

    janartylgan = baylanyspagan = 0
    jana_qatarlar: list[str] = []
    for j in jazbalar:
        if not j.olshem.toly and j.url:
            if (pid := karta.get(j.url)):
                j.olshem = api.olshem(pid)
                janartylgan += 1
            else:
                baylanyspagan += 1
        jana_qatarlar.append(j.json_qatar())

    if janartylgan:
        p.write_text("\n".join(jana_qatarlar) + "\n", encoding="utf-8")
    return janartylgan, baylanyspagan


def _cli(argv: list[str]) -> int:
    buiryq = argv[0] if argv else "komek"

    if buiryq == "token" and len(argv) > 1:
        jol = token_jaz(argv[1])
        print(f"Токен сақталды: {jol}\nБұл файл .gitignore ішінде.")
        return 0

    try:
        api = ThreadsApi()
    except ThreadsQate as e:
        print(e)
        return 1

    try:
        if buiryq == "posttar":
            for p in api.posttar():
                print(f"{p.kuni}  {p.id}  {p.mati[:60]!r}")
        elif buiryq == "janart":
            j, b = olshemderdi_janart(api)
            print(f"Жаңартылды: {j} жазба.")
            if b:
                print(f"Байланыспады: {b} (журналда url жоқ немесе пост табылмады).")
        else:
            print(
                "Қолданысы:\n"
                "  python3 -m lib.threads_api token <ТОКЕН>   токенді сақтау\n"
                "  python3 -m lib.threads_api posttar         посттарды көру\n"
                "  python3 -m lib.threads_api janart          журналды толтыру"
            )
            return 1
    except ThreadsQate as e:
        print(f"Қате: {e}")
        return 1
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(_cli(sys.argv[1:]))
