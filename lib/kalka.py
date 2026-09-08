"""Орысша калька, кеңсе тілі және аударма клишелерін табу.

Не істейді: сөздікке негізделген іздеу. Әр жазба — тіркес, оның қайдан
шыққаны және тірі баламасы. Threads — сөйлеу тіліне жақын алаң, ал кеңсе
тіркесі постты бірден «хабарламаға» айналдырады.

Не істемейді: бұл модуль мәтіннің мағынасын түсінбейді. Ол тек ҮМІТКЕР
тіркестерді белгілейді. Кейбір тіркес заңды контексте дұрыс болуы мүмкін
(мысалы, ресми құжат туралы жазып жатсаң, «қаулы қабылданды» — қалыпты).
Соңғы шешімді модель контекстке қарап қабылдайды.

Дереккөз: тіркестер тізімі қазақ тіліндегі редактура тәжірибесінен және
орыс тілінен калькаланған канцеляризмдердің жиі кездесетін үлгілерінен
жиналған. Әрқайсысында орыс тіліндегі түпнұсқасы көрсетілген.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

Sanat = Literal["kense", "kalka", "komekshi", "klishe", "quram"]

SANAT_ATY: dict[Sanat, str] = {
    "kense": "кеңсе тілі",
    "kalka": "орысша калька",
    "komekshi": "артық көмекші етістік",
    "klishe": "аударма/AI клишесі",
    "quram": "құрылымдық",
}


@dataclass(frozen=True)
class Jazba:
    """Сөздіктегі бір жазба."""

    ulgi: str          # regex
    sanat: Sanat
    balama: str        # тірі баламасы
    tupnusqa: str = "" # орысша түпнұсқасы, белгілі болса


# --- Сөздік ----------------------------------------------------------------
# Реті маңызды емес, бәрі бір өтуде тексеріледі.

SOZDIK: list[Jazba] = [
    # --- Кеңсе тілі: етістік орнына тіркес ---
    Jazba(r"болып\s+табылад\w*", "kense", "тікелей айт: «X — Y» немесе жай етістік", "является"),
    Jazba(r"болып\s+саналад\w*", "kense", "саналады / деп есептеледі", "считается"),
    Jazba(r"жүзеге\s+асыр\w*", "kense", "істеу, жасау, орындау, шығару", "осуществлять"),
    Jazba(r"іске\s+асыр\w*", "kense", "істеу, жасау, орындау", "реализовать"),
    Jazba(r"қамтамасыз\s+ет\w*", "kense", "беру, істеу, ұстау", "обеспечить"),
    Jazba(r"жүзеге\s+ас\w+", "kense", "болу, орындалу", "осуществляться"),
    Jazba(r"орын\s+алд\w*", "kense", "болды", "имело место"),
    Jazba(r"мүмкіндік\s+бер\w*", "kense", "«-а алады»: «көруге мүмкіндік береді» → «көре аласың»", "позволяет"),
    Jazba(r"әрекет\s+ет\w*", "kense", "істеу, жұмыс істеу", "действовать"),
    Jazba(r"қолданысқа\s+енгіз\w*", "kense", "қосу, іске қосу", "ввести в эксплуатацию"),
    Jazba(r"назарға\s+ал\w+\s+қажет", "kense", "ескеру керек", "необходимо учесть"),
    Jazba(r"талдау\s+өткіз\w*", "kense", "талдау жасау, талдау", "провести анализ"),
    Jazba(r"жұмыс(?:тар)?\s+жүргіз\w*", "kense", "жұмыс істеу", "проводить работы"),

    # --- Орысша калька: сөйлем құрылымы ---
    Jazba(r"аталған\s+", "kalka", "бұл, осы", "данный"),
    Jazba(r"\bберілген\s+(?:мәселе|сұрақ|жағдай|тақырып)", "kalka", "бұл, осы", "данный"),
    Jazba(r"барысында\b", "kalka", "кезінде, «-ғанда»", "в ходе"),
    Jazba(r"шеңберінде\b", "kalka", "ішінде, аясында", "в рамках"),
    Jazba(r"мақсатында\b", "kalka", "үшін", "в целях"),
    Jazba(r"тарапынан\b", "kalka", "«-дан/-нан»: «біз тарапынан» → «бізден»", "со стороны"),
    Jazba(r"негізінде\b", "kalka", "бойынша", "на основании"),
    Jazba(r"тұрғысынан\s+алғанда", "kalka", "жағынан", "с точки зрения"),
    Jazba(r"бір\s?қатар\b", "kalka", "бірнеше", "ряд"),
    Jazba(r"деген\s+сұрақ\s+туындайд\w*", "kalka", "сұрақ шығады / жай сұрақ қой", "возникает вопрос"),
    Jazba(r"жоғарыда\s+аталған", "kalka", "жоғарыдағы", "вышеуказанный"),
    Jazba(r"келесідей\b", "kalka", "мынадай", "следующим образом"),
    Jazba(r"төмендегідей\b", "kalka", "мынадай", "следующим образом"),
    Jazba(r"атап\s+айтқанда", "kalka", "мысалы", "а именно"),
    Jazba(r"осыған\s+байланысты", "kalka", "сондықтан", "в связи с этим"),
    Jazba(r"жоғары\s+деңгейде\b", "kalka", "жақсы, мықты", "на высоком уровне"),
    Jazba(r"қысқа\s+мерзім\s+ішінде", "kalka", "тез, жылдам", "в короткие сроки"),
    Jazba(r"бағыттал\w+\b", "kalka", "«-ға арналған» немесе тікелей етістік", "направленный"),

    # --- Артық көмекші етістік (қабаттасу) ---
    Jazba(r"болып\s+отыр\w*", "komekshi", "жай осы шақ: «керек болып отыр» → «керек»", "является/находится"),
    Jazba(r"болып\s+жатыр\w*", "komekshi", "жай осы шақ", ""),
    Jazba(r"келе\s+жатыр\w*", "komekshi", "тек қозғалыс мағынасында қалдыр", ""),
    Jazba(r"жасалын\w+", "komekshi", "«жасалды» — «-ла» мен «-ын» қабаттасқан, қос ырықсыз етіс", ""),
    Jazba(r"айтылын\w+", "komekshi", "«айтылды»", ""),
    Jazba(r"алын\w+\s+тастал\w+", "komekshi", "алынды, өшірілді", "было удалено"),

    # --- Аударма / AI клишесі ---
    Jazba(r"қазіргі\s+таңда", "klishe", "қазір", "на сегодняшний день"),
    Jazba(r"бүгінгі\s+таңда", "klishe", "бүгін, қазір", "на сегодняшний день"),
    Jazba(r"заманауи\s+әлемде", "klishe", "тастап кет — ақпарат жоқ", "в современном мире"),
    Jazba(r"қорытындылай\s+келе", "klishe", "тастап кет — Threads-те қорытынды абзац керек емес", "в заключение"),
    Jazba(r"жалпы\s+алғанда", "klishe", "тастап кет", "в целом"),
    Jazba(r"айта\s+кет\w+\s+(?:керек|жөн)", "klishe", "тастап кет, бірден айт", "стоит отметить"),
    Jazba(r"атап\s+өт\w+\s+(?:керек|жөн)", "klishe", "тастап кет", "следует отметить"),
    Jazba(r"маңызды\s+рөл\s+атқарад\w*", "klishe", "нақты не істейтінін жаз", "играет важную роль"),
    Jazba(r"үлкен\s+рөл\s+атқарад\w*", "klishe", "нақты не істейтінін жаз", "играет большую роль"),
    Jazba(r"ажырамас\s+бөлі\w+", "klishe", "тастап кет", "неотъемлемая часть"),
    Jazba(r"жаңа\s+деңгейге\s+көтер\w*", "klishe", "нақты нәтижені жаз", "вывести на новый уровень"),
    Jazba(r"әлеует\w*\s+аш\w+", "klishe", "нақты не өзгеретінін жаз", "раскрыть потенциал"),
    Jazba(r"тиімділікті\s+артты?р\w*", "klishe", "қанша пайызға артқанын жаз", "повысить эффективность"),
    Jazba(r"құрметті\s+(?:достар|оқырман\w*|әріптестер)", "klishe", "Threads-те сәлемдесу керек емес", "уважаемые"),
    Jazba(r"назарларыңызға\s+ұсынам\w*", "klishe", "бірден мазмұнға көш", "представляю вашему вниманию"),
    Jazba(r"терең\s+үңіл\w*", "klishe", "қарау, зерттеу", "delve / углубиться"),
]

_QURASTYRYLGAN = [(re.compile(j.ulgi, re.IGNORECASE), j) for j in SOZDIK]

# Threads посты үшін ұзын сөйлем шегі. Қазақ тілі жалғамалы, сондықтан
# сөз саны аз болса да таңба көп кетеді, ал есімше тізбегі оқуды баяулатады.
UZYN_SOILEM_SOZ = 18

SOILEM = re.compile(r"[^.!?\n]+[.!?]*")
SOZ = re.compile(r"[\wЀ-ӿ]+", re.UNICODE)
TRIADA = re.compile(r"([\wЀ-ӿ]+),\s+([\wЀ-ӿ]+)\s+және\s+([\wЀ-ӿ]+)", re.UNICODE)


@dataclass
class Tabylym:
    """Табылған бір мәселе."""

    tirkes: str
    sanat: Sanat
    balama: str
    tupnusqa: str
    orny: int

    def __str__(self) -> str:
        bas = f"«{self.tirkes}» — {SANAT_ATY[self.sanat]}"
        if self.tupnusqa:
            bas += f" (< {self.tupnusqa})"
        return f"{bas}\n    → {self.balama}"


@dataclass
class KalkaEsebi:
    soz_sany: int
    tabylymdar: list[Tabylym] = field(default_factory=list)
    quram_eskertuler: list[str] = field(default_factory=list)

    @property
    def tygyzdyq(self) -> float:
        """100 сөзге шаққандағы мәселе саны."""
        return len(self.tabylymdar) / self.soz_sany * 100 if self.soz_sany else 0.0

    @property
    def bagalau(self) -> str:
        t = self.tygyzdyq
        if t == 0:
            return "таза"
        if t < 2:
            return "жақсы"
        if t < 5:
            return "редактура керек"
        return "қайта жазу керек"

    def __str__(self) -> str:
        jol = [
            f"Сөз: {self.soz_sany} | табылған: {len(self.tabylymdar)} | "
            f"тығыздық: {self.tygyzdyq:.1f}/100 сөз | баға: {self.bagalau}"
        ]
        if self.tabylymdar:
            jol.append("")
            sanattar: dict[Sanat, list[Tabylym]] = {}
            for t in self.tabylymdar:
                sanattar.setdefault(t.sanat, []).append(t)
            for sanat, tizim in sanattar.items():
                jol.append(f"### {SANAT_ATY[sanat].capitalize()}")
                jol += [f"  {t}" for t in tizim]
                jol.append("")
        if self.quram_eskertuler:
            jol.append("### Құрылым")
            jol += [f"  {e}" for e in self.quram_eskertuler]
        if not self.tabylymdar and not self.quram_eskertuler:
            jol.append("\nКалька да, кеңсе тілі де табылмады.")
        return "\n".join(jol)


def _quram_tekseru(mati: str) -> list[str]:
    """Сөздікке кірмейтін құрылымдық белгілер."""
    eskertuler: list[str] = []

    for soilem in SOILEM.findall(mati):
        sozder = SOZ.findall(soilem)
        if len(sozder) > UZYN_SOILEM_SOZ:
            eskertuler.append(
                f"{len(sozder)} сөзді сөйлем ({UZYN_SOILEM_SOZ}-дан ұзын). "
                f"Threads-те екіге бөл: «{soilem.strip()[:50]}…»"
            )

    triadalar = TRIADA.findall(mati)
    if triadalar:
        for a, b, c in triadalar:
            eskertuler.append(
                f"Үштік тізбек: «{a}, {b} және {c}». Үш затты қатар тізу — "
                "аударма мен AI мәтінінің жиі белгісі. Біреуін таңда."
            )
    return eskertuler


def tekseru(mati: str) -> KalkaEsebi:
    """Мәтіндегі калька мен кеңсе тілін тексереді."""
    tabylymdar: list[Tabylym] = []
    for ulgi, jazba in _QURASTYRYLGAN:
        for m in ulgi.finditer(mati):
            tabylymdar.append(
                Tabylym(
                    tirkes=m.group().strip(),
                    sanat=jazba.sanat,
                    balama=jazba.balama,
                    tupnusqa=jazba.tupnusqa,
                    orny=m.start(),
                )
            )
    # Қабаттасқан сәйкестікті тазалау: бір орында бірнеше үлгі түссе,
    # ең ұзынын қалдырамыз («жүзеге асыру» «жүзеге ас»-тан артық).
    tabylymdar.sort(key=lambda t: (t.orny, -len(t.tirkes)))
    tazalar: list[Tabylym] = []
    ayaqtalgan = -1
    for t in tabylymdar:
        if t.orny < ayaqtalgan:
            continue
        tazalar.append(t)
        ayaqtalgan = t.orny + len(t.tirkes)
    tabylymdar = tazalar
    return KalkaEsebi(
        soz_sany=len(SOZ.findall(mati)),
        tabylymdar=tabylymdar,
        quram_eskertuler=_quram_tekseru(mati),
    )


if __name__ == "__main__":
    import sys

    mati = " ".join(sys.argv[1:]) or sys.stdin.read()
    print(tekseru(mati))
