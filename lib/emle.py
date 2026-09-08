"""Қазақ мәтінінің емлесін, әліпбиін және Threads шектеулерін тексеру.

Бұл модуль мәтіннің МАЗМҰНЫН бағаламайды — тек механикалық, автоматты түрде
тексерілетін нәрселерді қарайды. Стиль мен тон `references/` ішіндегі
ережелерде, оны модель өзі оқиды.

Ең маңызды тексеру — ГОМОГЛИФ. Латын `i` мен кирилл `і`, латын `a` мен кирилл
`а` экранда бірдей көрінеді, бірақ Unicode-та бөлек таңбалар. Қазақша жазғанда
пернетақта ауысып кетсе, сөз көзге дұрыс көрінеді, ал:

  * Threads/Instagram іздеуі ол сөзді таппайды,
  * хэштег басқа хэштегке айналады,
  * көшіріп қойған адамның мәтіні бұзылады.

Бұл — қазақ контентіндегі №1 үнсіз қате, сондықтан модуль оны бірінші тексереді.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Iterable, Literal

# --- Әліпби жиындары -------------------------------------------------------

# Қазақ кириллицасы (42 әріп).
QAZ_CYRILLIC = set("АӘБВГҒДЕЁЖЗИЙКҚЛМНҢОӨПРСТУҰҮФХҺЦЧШЩЪЫІЬЭЮЯ"
                   "аәбвгғдеёжзийкқлмнңоөпрстуұүфхһцчшщъыіьэюя")

# Тек қазақ тілінде бар әріптер. Мәтінде бұлардың болуы — қазақша екенінің белгісі.
QAZ_ONLY = set("әғқңөұүһіӘҒҚҢӨҰҮҺІ")

# Қазақтың төл сөздерінде кездеспейтін, тек кірме сөздерде жүретін әріптер.
# Көп болса — мәтін орысшадан аударылған немесе кірме сөзге толы деген белгі.
RUS_ONLY = set("ёъьэщцчфЁЪЬЭЩЦЧФ")

# Кирилл әрпіне ҰҚСАС латын әріптері. Кілт — латын, мән — дұрыс кирилл нұсқасы.
HOMOGLYPHS = {
    "A": "А", "B": "В", "C": "С", "E": "Е", "H": "Н", "I": "І", "K": "К",
    "M": "М", "O": "О", "P": "Р", "T": "Т", "X": "Х", "Y": "У",
    "a": "а", "c": "с", "e": "е", "i": "і", "o": "о", "p": "р", "x": "х",
    "y": "у",
}

# Кері бағыт: кирилл әрпі латын сөзінің ішіне кіріп кетсе.
# «Clаudе» (кирилл а мен е) — латын i-дегідей үнсіз қате, тек бағыты басқа.
KERI_HOMOGLYPHS = {kirill: latyn for latyn, kirill in HOMOGLYPHS.items()}

LATIN_LETTER = re.compile(r"[A-Za-z]")
CYRILLIC_LETTER = re.compile(r"[Ѐ-ӿ]")
WORD = re.compile(r"[\wЀ-ӿ]+", re.UNICODE)
HASHTAG = re.compile(r"(?<!\w)#[\wЀ-ӿ]+", re.UNICODE)
URL = re.compile(r"https?://\S+")

# Threads шектеулері.
POST_LIMIT = 500
LONGFORM_LIMIT = 10_000
HASHTAG_LIMIT = 1

Severity = Literal["qate", "eskertu", "kenes"]


@dataclass
class Belgi:
    """Бір тексеру нәтижесі."""

    turi: str
    dengei: Severity
    habar: str
    uzindi: str = ""

    def __str__(self) -> str:
        belgi = {"qate": "ҚАТЕ", "eskertu": "ЕСКЕРТУ", "kenes": "КЕҢЕС"}[self.dengei]
        bolim = f"[{belgi}] {self.turi}: {self.habar}"
        return f"{bolim}\n         → {self.uzindi}" if self.uzindi else bolim


@dataclass
class EmleEsebi:
    """Толық тексеру есебі."""

    tanba_sany: int
    soz_sany: int
    hashtag_sany: int
    qazaq_arip_ulesi: float
    belgiler: list[Belgi] = field(default_factory=list)

    @property
    def qateler(self) -> list[Belgi]:
        return [b for b in self.belgiler if b.dengei == "qate"]

    @property
    def taza(self) -> bool:
        return not self.qateler

    def __str__(self) -> str:
        bas = (
            f"Таңба: {self.tanba_sany}/{POST_LIMIT} | сөз: {self.soz_sany} | "
            f"хэштег: {self.hashtag_sany} | қазақ әрпінің үлесі: "
            f"{self.qazaq_arip_ulesi:.1%}"
        )
        if not self.belgiler:
            return bas + "\n\nТаза. Ешқандай механикалық қате табылмады."
        return bas + "\n\n" + "\n".join(str(b) for b in self.belgiler)


def _kontekst(mati: str, orny: int, radius: int = 24) -> str:
    bas = max(0, orny - radius)
    ayaq = min(len(mati), orny + radius)
    uzindi = mati[bas:ayaq].replace("\n", " ")
    return f"…{uzindi}…" if bas > 0 or ayaq < len(mati) else uzindi


def _talda_aralas(soz: str) -> tuple[str, str, list[str]] | None:
    """Аралас сөзді талдап, қай бағытқа түзету керегін шешеді.

    Қайтарады: (басым_жазу, түзетілген_сөз, ауысатын_таңбалар) немесе None.

    Шешім қалай қабылданады: әр жазудың БІРМӘНДІ әріптерін санаймыз —
    яғни екінші жазуда ұқсасы жоқ әріптерді (латын `l`, `d`, `u`; кирилл
    `б`, `ж`, `з`). Қай жазуда бірмәнді әріп болса, сөз соныкі, ал екінші
    жазудың әріптері — кіріп кеткен бөгде таңба.

    None қайтарылады, егер:
      * екі жақта да бірмәнді әріп болса (шын аралас жазу: «PRщик»),
      * не екі жақта да болмаса (шешуге дерек жоқ),
      * не азшылықтың ішінде ұқсасы жоқ әріп болса (автоматты түзету қате
        нәтиже беретін еді).
    """
    latyn = [c for c in soz if LATIN_LETTER.match(c)]
    kirill = [c for c in soz if CYRILLIC_LETTER.match(c)]
    if not latyn or not kirill:
        return None

    latyn_birmandi = [c for c in latyn if c not in HOMOGLYPHS]
    kirill_birmandi = [c for c in kirill if c not in KERI_HOMOGLYPHS]

    if latyn_birmandi and not kirill_birmandi:
        basym, azshylyq, karta = "латын", kirill, KERI_HOMOGLYPHS
    elif kirill_birmandi and not latyn_birmandi:
        basym, azshylyq, karta = "кирилл", latyn, HOMOGLYPHS
    else:
        return None

    if any(c not in karta for c in azshylyq):
        return None  # автоматты түзетуге келмейді

    auysatyn = sorted(set(azshylyq))
    tuzetilgen = "".join(karta.get(c, c) if c in azshylyq else c for c in soz)
    return basym, tuzetilgen, auysatyn


def gomoglif_tabu(mati: str) -> list[Belgi]:
    """Бір сөздің ішінде екі жазудың араласып кеткенін табады.

    Екі бағытты да ұстайды:
      * кирилл сөзіне кіріп кеткен латын әрпі («бiр» — латын i),
      * латын сөзіне кіріп кеткен кирилл әрпі («Clаudе» — кирилл а, е).

    Таза латын сөзі (AI, Claude, startup) — заңды кодты ауыстыру, оған
    тиіспейміз.
    """
    belgiler: list[Belgi] = []
    for m in WORD.finditer(mati):
        soz = m.group()
        shesim = _talda_aralas(soz)

        if shesim is None:
            # Аралас, бірақ автоматты шешуге келмейді.
            if LATIN_LETTER.search(soz) and CYRILLIC_LETTER.search(soz):
                belgiler.append(
                    Belgi(
                        turi="аралас-жазу",
                        dengei="eskertu",
                        habar=(
                            f"«{soz}» сөзінде латын мен кирилл араласқан, бірақ "
                            "қайсысы дұрыс екені анық емес — қолмен қара. "
                            "Кірме терминге қосымша жалғасаң, дефис қой: "
                            "«AI-ды», «PR-ы»."
                        ),
                        uzindi=_kontekst(mati, m.start()),
                    )
                )
            continue

        basym, tuzetilgen, auysatyn = shesim
        bogde = "кирилл" if basym == "латын" else "латын"
        karta = KERI_HOMOGLYPHS if basym == "латын" else HOMOGLYPHS
        belgiler.append(
            Belgi(
                turi="гомоглиф",
                dengei="qate",
                habar=(
                    f"«{soz}» — {basym} сөзі, бірақ ішінде {bogde} әрпі бар: "
                    + ", ".join(f"«{c}» → «{karta[c]}»" for c in auysatyn)
                    + f". Дұрысы: «{tuzetilgen}». Көзге бірдей көрінеді, "
                    "бірақ іздеу таппайды."
                ),
                uzindi=_kontekst(mati, m.start()),
            )
        )
    return belgiler


def alipbi_tekseru(mati: str) -> tuple[float, list[Belgi]]:
    """Мәтіннің шынымен қазақша екенін және әріп қолданысын бағалайды."""
    belgiler: list[Belgi] = []
    ariptrer = [c for c in mati if c.isalpha()]
    if not ariptrer:
        return 0.0, belgiler

    kirill_sany = sum(1 for c in ariptrer if c in QAZ_CYRILLIC)
    qaz_only_sany = sum(1 for c in ariptrer if c in QAZ_ONLY)
    ules = qaz_only_sany / kirill_sany if kirill_sany else 0.0

    # Қазақша мәтінде әә/ғ/қ/ң/ө/ұ/ү/і әріптері әдетте 8-15% құрайды.
    # 3%-дан төмен болса — мәтін орысша немесе аудармаға тым жақын.
    if kirill_sany >= 40 and ules < 0.03:
        belgiler.append(
            Belgi(
                turi="әліпби",
                dengei="eskertu",
                habar=(
                    f"Қазаққа тән әріптердің үлесі {ules:.1%} ғана "
                    "(қалыпты мәтінде 8-15%). Мәтін орысшадан тікелей "
                    "аударылған немесе кірме сөзге толы болуы мүмкін."
                ),
            )
        )

    rus_sany = sum(1 for c in ariptrer if c in RUS_ONLY)
    if kirill_sany >= 40 and rus_sany / kirill_sany > 0.04:
        belgiler.append(
            Belgi(
                turi="әліпби",
                dengei="kenes",
                habar=(
                    f"Тек кірме сөзде жүретін әріптер (ё, ъ, ь, э, щ, ц, ч, ф) "
                    f"{rus_sany} рет кездесті. Қазақша баламасы бар ма, тексер."
                ),
            )
        )
    return ules, belgiler


def threads_shektuleri(mati: str, uzin_forma: bool = False) -> list[Belgi]:
    """Threads платформасының қатты шектеулерін тексереді."""
    belgiler: list[Belgi] = []
    shek = LONGFORM_LIMIT if uzin_forma else POST_LIMIT
    uzyndyq = len(mati)

    if uzyndyq > shek:
        belgiler.append(
            Belgi(
                turi="көлем",
                dengei="qate",
                habar=(
                    f"{uzyndyq} таңба, шегі {shek}. "
                    f"{uzyndyq - shek} таңба артық. Қысқарт немесе тредке бөл."
                ),
            )
        )
    elif not uzin_forma and uzyndyq > POST_LIMIT * 0.92:
        belgiler.append(
            Belgi(
                turi="көлем",
                dengei="kenes",
                habar=(
                    f"{uzyndyq}/{POST_LIMIT} таңба. Шекке тым жақын: эмодзи "
                    "немесе сілтеме қоссаң, асып кетесің."
                ),
            )
        )

    hashtagter = HASHTAG.findall(mati)
    if len(hashtagter) > HASHTAG_LIMIT:
        belgiler.append(
            Belgi(
                turi="хэштег",
                dengei="qate",
                habar=(
                    f"{len(hashtagter)} хэштег: {', '.join(hashtagter)}. "
                    "Threads біреуін ғана қабылдайды, қалғанын өзі алып тастайды."
                ),
            )
        )

    siltemeler = URL.findall(mati)
    if siltemeler:
        birinshi_jol = mati.split("\n", 1)[0]
        if any(s in birinshi_jol for s in siltemeler):
            belgiler.append(
                Belgi(
                    turi="сілтеме",
                    dengei="eskertu",
                    habar=(
                        "Сыртқы сілтеме бірінші жолда тұр. Threads алгоритмі "
                        "мұндай постың қамтуын төмендетеді — сілтемені "
                        "соңына, жауапқа немесе тредтің 2-постына көшір."
                    ),
                )
            )
    return belgiler


def _emoji_sany(mati: str) -> int:
    return sum(1 for c in mati if unicodedata.category(c) == "So")


def tekseru(mati: str, uzin_forma: bool = False) -> EmleEsebi:
    """Мәтінді толық тексеріп, есеп қайтарады.

    Args:
        mati: Тексерілетін Threads посты немесе тред блогы.
        uzin_forma: Мәтін тіркемесі бар ұзын пост (10 000 таңба) болса True.
    """
    belgiler: list[Belgi] = []
    belgiler += gomoglif_tabu(mati)
    ules, alipbi_belgileri = alipbi_tekseru(mati)
    belgiler += alipbi_belgileri
    belgiler += threads_shektuleri(mati, uzin_forma=uzin_forma)

    emoji = _emoji_sany(mati)
    if emoji > 2:
        belgiler.append(
            Belgi(
                turi="эмодзи",
                dengei="kenes",
                habar=f"{emoji} эмодзи. Постқа 0-2 жеткілікті, көбі жарнамаға ұқсатады.",
            )
        )

    dengei_reti = {"qate": 0, "eskertu": 1, "kenes": 2}
    belgiler.sort(key=lambda b: dengei_reti[b.dengei])

    return EmleEsebi(
        tanba_sany=len(mati),
        soz_sany=len(WORD.findall(mati)),
        hashtag_sany=len(HASHTAG.findall(mati)),
        qazaq_arip_ulesi=ules,
        belgiler=belgiler,
    )


def tuzetu(mati: str) -> str:
    """Гомоглифтерді автоматты түрде түзетеді. Басқасына тиіспейді.

    Тек аралас сөздің ішіндегі латын әрпін ауыстырады, сондықтан `Claude`,
    `AI`, `startup` сияқты таза латын сөздері сол күйі қалады.
    """
    def _auystyru(m: re.Match) -> str:
        shesim = _talda_aralas(m.group())
        return m.group() if shesim is None else shesim[1]

    return WORD.sub(_auystyru, mati)


def _cli(argv: Iterable[str]) -> int:
    import sys

    args = list(argv)
    if not args:
        mati = sys.stdin.read()
    else:
        mati = " ".join(args)
    print(tekseru(mati))
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(_cli(sys.argv[1:]))
