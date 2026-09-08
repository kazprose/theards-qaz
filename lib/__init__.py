"""Қазақша Threads шеберліктерінің ортақ көмекші кітапханасы.

Модульдер:
    emle       — гомоглиф, әліпби, Threads шектеулері
    kalka      — орысша калька, кеңсе тілі, аударма клишелері
    translit   — кирилл ↔ латын (QazLat 2021), хэштег нұсқалары
    url_parser — Threads сілтемелерін талдау
    maquldau   — драфтты мақұлдау карточкасы
    undestik   — дауысты үндестігі (қосымша дұрыс жалғанған ба)
    jariyalau  — қолмен / өзіндік жариялау қабаты
    audit      — emle + kalka + undestik біріктірілген тексеру
    jurnal     — пост журналы: не жарияланды, не болды
    profil     — дауыс профилі: кімсің, аудиторияң кім, қалай сөйлейсің
    threads_api — Threads-тің ресми Graph API клиенті

Импорт жалқау (PEP 562): `python3 -m lib.emle` шақырғанда пакет ішкі
модульдерді алдын ала жүктемейді, сондықтан runpy ескертуі шықпайды.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

# Көпшілікке ашық ат → (модуль, сол модульдегі ат)
_KARTA: dict[str, tuple[str, str]] = {
    "emle_tekseru": ("emle", "tekseru"),
    "gomoglif_tuzetu": ("emle", "tuzetu"),
    "EmleEsebi": ("emle", "EmleEsebi"),
    "Belgi": ("emle", "Belgi"),
    "kalka_tekseru": ("kalka", "tekseru"),
    "KalkaEsebi": ("kalka", "KalkaEsebi"),
    "Tabylym": ("kalka", "Tabylym"),
    "latynga": ("translit", "latynga"),
    "hashtag": ("translit", "hashtag"),
    "hashtag_nusqalary": ("translit", "hashtag_nusqalary"),
    "url_talda": ("url_parser", "talda"),
    "kartochka": ("maquldau", "kartochka"),
    "jariyala": ("jariyalau", "jariyala"),
    "qabat": ("jariyalau", "qabat"),
    "qoldan_habar": ("jariyalau", "qoldan_habar"),
    "undestik_tekseru": ("undestik", "tekseru"),
    "Undestik": ("undestik", "Undestik"),
    "tolyq": ("audit", "tolyq"),
    "ToliqEsep": ("audit", "ToliqEsep"),
    "Profil": ("profil", "Profil"),
    "profil_oqy": ("profil", "oqy"),
    "profil_ulgi": ("profil", "ulgi"),
    "profil_jaz": ("profil", "jaz"),
    "profil_saikestik": ("profil", "saikestik"),
    "registr_tabu": ("profil", "registr_tabu"),
    "Jazba": ("jurnal", "Jazba"),
    "Olshem": ("jurnal", "Olshem"),
    "jurnal_jaz": ("jurnal", "jaz"),
    "jurnal_oqy": ("jurnal", "oqy"),
    "jurnal_esep": ("jurnal", "esep"),
    "jurnal_qorytu": ("jurnal", "qorytu"),
    "bolzham": ("jurnal", "bolzham"),
    "tauekel": ("jurnal", "tauekel"),
    "belgiler_al": ("jurnal", "belgiler_al"),
    "ThreadsApi": ("threads_api", "ThreadsApi"),
    "ThreadsQate": ("threads_api", "ThreadsQate"),
    "token_oqy": ("threads_api", "token_oqy"),
    "token_jaz": ("threads_api", "token_jaz"),
    "olshemderdi_janart": ("threads_api", "olshemderdi_janart"),
    "avto_jariyala": ("jariyalau", "avto_jariyala"),
    "avto_rejim": ("jariyalau", "avto_rejim"),
}

__all__ = list(_KARTA)


def __getattr__(at: str) -> Any:
    try:
        modul_aty, ishki_at = _KARTA[at]
    except KeyError:
        raise AttributeError(f"lib пакетінде «{at}» жоқ") from None
    from importlib import import_module

    return getattr(import_module(f".{modul_aty}", __name__), ishki_at)


def __dir__() -> list[str]:
    return sorted(__all__)


if TYPE_CHECKING:  # тек редактор мен тип тексергішке
    from .audit import ToliqEsep, tolyq
    from .emle import Belgi, EmleEsebi
    from .emle import tekseru as emle_tekseru
    from .emle import tuzetu as gomoglif_tuzetu
    from .jariyalau import avto_jariyala, avto_rejim, jariyala, qabat, qoldan_habar
    from .jurnal import Jazba, Olshem
    from .jurnal import esep as jurnal_esep
    from .jurnal import jaz as jurnal_jaz
    from .jurnal import oqy as jurnal_oqy
    from .jurnal import belgiler_al, bolzham, qorytu as jurnal_qorytu, tauekel
    from .profil import Profil, registr_tabu
    from .profil import jaz as profil_jaz
    from .profil import oqy as profil_oqy
    from .profil import saikestik as profil_saikestik
    from .profil import ulgi as profil_ulgi
    from .threads_api import (ThreadsApi, ThreadsQate, olshemderdi_janart,
                              token_jaz, token_oqy)
    from .kalka import KalkaEsebi, Tabylym
    from .kalka import tekseru as kalka_tekseru
    from .maquldau import kartochka
    from .translit import hashtag, hashtag_nusqalary, latynga
    from .undestik import Undestik
    from .undestik import tekseru as undestik_tekseru
    from .url_parser import talda as url_talda
