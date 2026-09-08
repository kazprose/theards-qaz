"""Кирилл ↔ латын транслитерациясы (QazLat 2021) және хэштег дайындау.

Не үшін керек: Threads пен Instagram іздеуі хэштегті таңбамен дәл салыстырады.
`#қазақстан` пен `#qazaqstan` — екі бөлек хэштег, аудиториясы да бөлек.
Постқа бір ғана хэштег сыятындықтан, қайсысын таңдау — нақты шешім, сондықтан
екі нұсқасын да көрсете білу керек.

Әліпби: 2021 жылғы 28 қаңтарда бекітілген умлаут/бревис нұсқасы
(A Ä B D E F G Ğ H I İ J K L M N Ñ O Ö P Q R S Ş T U Ū Ü V Y Z).
Диакритиканы қолдамайтын жерге `ascii_qauipsiz=True` бер.
"""
from __future__ import annotations

import re

# Реті маңызды: көп таңбалы сәйкестік бұрын тұруы керек.
QAZLAT: list[tuple[str, str]] = [
    ("ю", "iu"), ("я", "ia"), ("ц", "ts"), ("ч", "ch"), ("щ", "shsh"),
    ("а", "a"), ("ә", "ä"), ("б", "b"), ("в", "v"), ("г", "g"), ("ғ", "ğ"),
    ("д", "d"), ("е", "e"), ("ё", "io"), ("ж", "j"), ("з", "z"), ("и", "i"),
    ("й", "i"), ("к", "k"), ("қ", "q"), ("л", "l"), ("м", "m"), ("н", "n"),
    ("ң", "ñ"), ("о", "o"), ("ө", "ö"), ("п", "p"), ("р", "r"), ("с", "s"),
    ("т", "t"), ("у", "u"), ("ұ", "ū"), ("ү", "ü"), ("ф", "f"), ("х", "h"),
    ("һ", "h"), ("ш", "ş"), ("ы", "y"), ("і", "i"), ("э", "e"),
    ("ъ", ""), ("ь", ""),
]

# Диакритикасыз баламасы — хэштег пен URL үшін.
_ASCII_JUPTAR = {"ä": "a", "ğ": "g", "ñ": "n", "ö": "o",
                 "ş": "s", "ū": "u", "ü": "u", "ı": "i"}
ASCII_BALAMA = str.maketrans(
    {**_ASCII_JUPTAR, **{k.upper(): v.upper() for k, v in _ASCII_JUPTAR.items()}}
)

_JIYN = {k: v for k, v in QAZLAT}


def latynga(mati: str, ascii_qauipsiz: bool = False) -> str:
    """Кирилл мәтінін QazLat 2021 латынына аударады.

    Args:
        mati: Кириллицадағы мәтін. Латын әріптері мен цифрлар сол күйі қалады.
        ascii_qauipsiz: True болса, диакритика ASCII-ға түсіріледі
            (ä→a, ğ→g, ñ→n, ö→o, ş→s, ū→u, ü→u). Хэштегке осыны қолдан.
    """
    natije: list[str] = []
    for tanba in mati:
        toment = tanba.lower()
        if toment in _JIYN:
            aud = _JIYN[toment]
            natije.append(aud.capitalize() if tanba.isupper() and aud else aud)
        else:
            natije.append(tanba)
    shyq = "".join(natije)
    return shyq.translate(ASCII_BALAMA) if ascii_qauipsiz else shyq


def hashtag(soz: str, latyn: bool = False) -> str:
    """Сөзді жарамды хэштегке айналдырады.

    Бос орын, дефис пен тыныс белгісі алынып тасталады. Threads хэштегте
    әріп пен цифрды ғана қабылдайды.
    """
    taza = re.sub(r"[^\wЀ-ӿ]+", "", soz, flags=re.UNICODE)
    if latyn:
        taza = latynga(taza, ascii_qauipsiz=True)
    return "#" + taza.lower()


def hashtag_nusqalary(soz: str) -> dict[str, str]:
    """Бір ұғымның екі хэштег нұсқасын қайтарады, таңдау үшін.

    Қайсысын алу керек:
      * кирилл — аудиторияң қазақша жазатын, жергілікті болса,
      * латын  — халықаралық не диаспоралық аудиторияға шықсаң.
    Екеуін қатар қоюға болмайды: Threads бір ғана хэштегті қабылдайды.
    """
    return {
        "кирилл": hashtag(soz),
        "латын": hashtag(soz, latyn=True),
    }


if __name__ == "__main__":
    import sys

    mati = " ".join(sys.argv[1:]) or sys.stdin.read().strip()
    print("Латын (QazLat):", latynga(mati))
    print("Латын (ASCII): ", latynga(mati, ascii_qauipsiz=True))
    print("Хэштег:        ", hashtag_nusqalary(mati))
