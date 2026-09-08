"""Threads сілтемелерін талдау.

Threads екі доменде жүреді: `threads.net` (бастапқы) және `threads.com`
(жаңасы). Екеуі бір постқа апарады, сондықтан бәрін `threads.com`-ға
қалыпқа келтіреміз.

Пост идентификаторы — base64 тәрізді қысқа код (мысалы `C8H9abcDEf_`),
сандық id емес. Quote post пен жай посттың сілтемесі бірдей: айырмашылық
сілтемеде емес, пайдаланушының не істейтінінде.
"""
from __future__ import annotations

import re
from typing import Literal, TypedDict

TURI = Literal["post", "profil"]

POST_ULGI = re.compile(
    r"^https?://(?:www\.)?threads\.(?:net|com)/@(?P<handle>[\w.]+)/post/(?P<kod>[\w-]+)",
    re.IGNORECASE,
)
PROFIL_ULGI = re.compile(
    r"^https?://(?:www\.)?threads\.(?:net|com)/@(?P<handle>[\w.]+)/?$",
    re.IGNORECASE,
)


class Siltem(TypedDict):
    handle: str
    post_id: str | None
    turi: TURI
    qalypty_url: str


def talda(url: str) -> Siltem:
    """Threads сілтемесін бөлшектейді.

    Raises:
        ValueError: сілтеме Threads постына да, профиліне де ұқсамаса.
    """
    url = url.strip()

    m = POST_ULGI.match(url)
    if m:
        handle, kod = m.group("handle"), m.group("kod")
        return Siltem(
            handle=handle,
            post_id=kod,
            turi="post",
            qalypty_url=f"https://www.threads.com/@{handle}/post/{kod}",
        )

    m = PROFIL_ULGI.match(url)
    if m:
        handle = m.group("handle")
        return Siltem(
            handle=handle,
            post_id=None,
            turi="profil",
            qalypty_url=f"https://www.threads.com/@{handle}",
        )

    raise ValueError(
        f"Threads сілтемесі танылмады: {url!r}. "
        "Күтілетін пішім: https://www.threads.com/@handle/post/KOD "
        "немесе https://www.threads.com/@handle"
    )


if __name__ == "__main__":
    import sys

    for url in sys.argv[1:]:
        try:
            print(talda(url))
        except ValueError as e:
            print(f"қате: {e}")
