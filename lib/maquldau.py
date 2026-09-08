"""Мақұлдау қақпасы.

Threads-ке ештеңе жарияламас бұрын, әр шеберлік драфтты пайдаланушыға
көрсетіп, нақты рұқсат алуы керек. Бұл файл сол драфтты бірыңғай пішінде
шығарады.

Маңызды: бұл — КЕЛІСІМ қабаты, техникалық тосқауыл емес. Кодта жариялауды
блоктайтын механизм жоқ, ережені модель өзі ұстайды. Сондықтан ережені
`SKILL.md` файлдарында да қайталап жазамыз.
"""
from __future__ import annotations

from typing import Optional

TURLERI = {
    "post": "жеке пост",
    "tred": "тред",
    "jauap": "жауап",
    "dayekshe": "дәйексөз посты (quote)",
}


def kartochka(
    *,
    turi: str,
    mati: str,
    nysana_url: Optional[str] = None,
    hook_kody: Optional[str] = None,
    qosymsha: Optional[dict[str, object]] = None,
) -> str:
    """Мақұлдауға арналған драфт карточкасын құрастырады.

    Args:
        turi: "post" | "tred" | "jauap" | "dayekshe".
        mati: Драфттың толық мәтіні. Тред болса, посттар `---` арқылы бөлінеді.
        nysana_url: Жауап/дәйексөз болса — түпнұсқа посттың сілтемесі.
        hook_kody: Қолданылған hook формуласының коды (мысалы, "Q3").
        qosymsha: Карточкаға қосылатын кез келген қосымша ақпарат.
    """
    posttar = [b.strip() for b in mati.split("\n---\n")] if "\n---\n" in mati else [mati]

    jol = [f"## Драфт дайын — {TURLERI.get(turi, turi)}", ""]
    if nysana_url:
        jol.append(f"**Нысана:** {nysana_url}")
    if hook_kody:
        jol.append(f"**Формула:** {hook_kody}")
    if len(posttar) > 1:
        jol.append(f"**Пост саны:** {len(posttar)}")
    jol.append("")

    for i, post in enumerate(posttar, 1):
        atau = f"**{i}-пост** ({len(post)}/500 таңба)" if len(posttar) > 1 \
            else f"**Мәтін** ({len(post)}/500 таңба)"
        jol.append(atau)
        jol.append("")
        jol += [f"> {q}" for q in (post.splitlines() or [""])]
        jol.append("")

    if qosymsha:
        jol.append("**Қосымша:**")
        jol += [f"- **{k}**: {v}" for k, v in qosymsha.items()]
        jol.append("")

    jol.append("Жариялау үшін **иә** немесе **қой** деп жаз, әйтпесе өзгертуді айт.")
    return "\n".join(jol)
