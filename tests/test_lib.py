"""lib/ модульдерінің тесттері. Сыртқы тәуелділік жоқ, unittest қана."""
import pathlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib import (audit, emle, jariyalau, jurnal, kalka, maquldau, profil,
                 translit, undestik, url_parser)


class GomoglifTest(unittest.TestCase):
    def test_latyn_i_tabylady(self):
        # «Бiз» — латын i-мен жазылған
        esep = emle.tekseru("Бiз бүгін бастадық")
        turleri = [b.turi for b in esep.belgiler]
        self.assertIn("гомоглиф", turleri)

    def test_taza_matinde_gomoglif_joq(self):
        esep = emle.tekseru("Біз бүгін бастадық")
        self.assertNotIn("гомоглиф", [b.turi for b in esep.belgiler])

    def test_taza_latyn_sozine_timeidi(self):
        # Claude, AI — таза латын, оларға тиюге болмайды
        self.assertEqual(emle.tuzetu("Claude мен AI"), "Claude мен AI")

    def test_tuzetu_aralasqan_sozdi_tuzetedi(self):
        self.assertEqual(emle.tuzetu("Бiз"), "Біз")

    def test_gomoglif_kartasy_kirillge_aparady(self):
        for latyn, kirill in emle.HOMOGLYPHS.items():
            self.assertTrue(latyn.isascii(), latyn)
            self.assertFalse(kirill.isascii(), kirill)


class ShektuTest(unittest.TestCase):
    def test_500_tanbadan_asqanda_qate(self):
        esep = emle.tekseru("а" * 501)
        self.assertFalse(esep.taza)
        self.assertIn("көлем", [b.turi for b in esep.qateler])

    def test_uzin_forma_10000ga_deiin_ruqsat(self):
        esep = emle.tekseru("а" * 501, uzin_forma=True)
        self.assertNotIn("көлем", [b.turi for b in esep.qateler])

    def test_eki_hashtag_qate(self):
        esep = emle.tekseru("мәтін #бірінші #екінші")
        self.assertIn("хэштег", [b.turi for b in esep.qateler])

    def test_bir_hashtag_duris(self):
        esep = emle.tekseru("мәтін #бірінші")
        self.assertNotIn("хэштег", [b.turi for b in esep.qateler])


class KalkaTest(unittest.TestCase):
    def test_kense_tili_tabylady(self):
        esep = kalka.tekseru("Бұл біздің мақсатымыз болып табылады")
        self.assertTrue(any("болып табылады" in t.tirkes for t in esep.tabylymdar))

    def test_qabattasqan_ulgi_bir_ret_qana(self):
        # «жүзеге асыру» екі үлгіге сәйкес келеді, бірақ бір рет шығуы керек
        esep = kalka.tekseru("жобаны жүзеге асыру")
        self.assertEqual(len(esep.tabylymdar), 1)
        self.assertEqual(esep.tabylymdar[0].tirkes, "жүзеге асыру")

    def test_ushtik_tizbek(self):
        esep = kalka.tekseru("Жылдам, тиімді және сенімді шешім.")
        self.assertTrue(any("Үштік" in e for e in esep.quram_eskertuler))

    def test_taza_mati(self):
        esep = kalka.tekseru("Кеше жаңа фича шығардық. Нәтиже жақсы.")
        self.assertEqual(esep.tabylymdar, [])
        self.assertEqual(esep.bagalau, "таза")

    def test_barlyq_ulgi_qurastyrylady(self):
        import re
        for j in kalka.SOZDIK:
            re.compile(j.ulgi)  # қате үлгі болса, осында құлайды


class TranslitTest(unittest.TestCase):
    def test_qazlat(self):
        self.assertEqual(translit.latynga("Қазақстан"), "Qazaqstan")

    def test_ascii_qauipsiz(self):
        self.assertTrue(translit.latynga("Әсем", ascii_qauipsiz=True).isascii())

    def test_hashtag_eki_nusqa(self):
        n = translit.hashtag_nusqalary("қазақ тілі")
        self.assertEqual(n["кирилл"], "#қазақтілі")
        self.assertTrue(n["латын"].isascii())

    def test_latyn_arip_ozgermeidi(self):
        self.assertEqual(translit.latynga("AI"), "AI")


class UrlTest(unittest.TestCase):
    def test_post_url(self):
        r = url_parser.talda("https://www.threads.net/@zuck/post/C8H9abcDEf_")
        self.assertEqual(r["handle"], "zuck")
        self.assertEqual(r["post_id"], "C8H9abcDEf_")
        self.assertEqual(r["turi"], "post")
        self.assertIn("threads.com", r["qalypty_url"])

    def test_profil_url(self):
        r = url_parser.talda("https://threads.com/@abai")
        self.assertEqual(r["turi"], "profil")
        self.assertIsNone(r["post_id"])

    def test_jaramsyz_url(self):
        with self.assertRaises(ValueError):
            url_parser.talda("https://example.com/@abai")


class JariyalauTest(unittest.TestCase):
    def test_adepki_qabat_qoldan(self):
        self.assertEqual(jariyalau.qabat(), "qoldan")

    def test_jauap_arqashan_qoldan(self):
        r = jariyalau.jariyala("jauap", mati="сынақ", nysana_url="https://x")
        self.assertEqual(r["qabat"], "qoldan")

    def test_dayekshe_arqashan_qoldan(self):
        r = jariyalau.jariyala("dayekshe", mati="сынақ", nysana_url="https://x")
        self.assertEqual(r["qabat"], "qoldan")


class MaquldauTest(unittest.TestCase):
    def test_kartochka_soragy_bar(self):
        k = maquldau.kartochka(turi="post", mati="сынақ")
        self.assertIn("иә", k)

    def test_tred_posttary_bolinedi(self):
        k = maquldau.kartochka(turi="tred", mati="бірінші\n---\nекінші")
        self.assertIn("Пост саны:** 2", k)


class AuditTest(unittest.TestCase):
    def test_qate_bar_matin_jiberilmeidi(self):
        r = audit.tolyq("Бiз бастадық")  # латын i
        self.assertFalse(r.joneltuge_dayin)

    def test_taza_matin_jiberiledi(self):
        r = audit.tolyq("Кеше жаңа фича шығардық.")
        self.assertTrue(r.joneltuge_dayin)


class KeriGomoglifTest(unittest.TestCase):
    """Латын сөзінің ішіне кирилл әрпі кіріп кетсе де ұстау керек."""

    BUZYQ = "Cl" + chr(0x430) + "ud" + chr(0x435)  # Clаudе — кирилл а мен е

    def test_keri_bagyt_tabylady(self):
        self.assertIn("гомоглиф", [b.turi for b in emle.gomoglif_tabu(self.BUZYQ)])

    def test_keri_bagyt_latynga_tuzetiledi(self):
        # Бұрын кодтың бағыты бір жақты болғандықтан, сөз одан бетер
        # кириллге айналып кететін. Енді таза латынға оралуы керек.
        tuzetilgen = emle.tuzetu(self.BUZYQ)
        self.assertEqual(tuzetilgen, "Claude")
        self.assertTrue(tuzetilgen.isascii())

    def test_shyn_aralas_soz_avtomatty_tuzetilmeidi(self):
        # «PRщик» — екі жақта да бірмәнді әріп бар, шешуге дерек жоқ.
        self.assertEqual(emle.tuzetu("PRщик"), "PRщик")
        self.assertEqual(
            [b.turi for b in emle.gomoglif_tabu("PRщик")], ["аралас-жазу"]
        )

    def test_keri_karta_toly(self):
        for kirill, latyn in emle.KERI_HOMOGLYPHS.items():
            self.assertEqual(emle.HOMOGLYPHS[latyn], kirill)


class UndestikTest(unittest.TestCase):
    BUZYQ = ["дедлайнге", "релизға", "стартапке", "фидбекқа"]
    DURYS = [
        "дедлайнға", "релизге", "стартапқа", "фидбекке", "балалар", "үйде",
        "қалада", "келді", "жалды", "адамдар", "кітапты", "мектепте",
        "жеті", "алты", "терезеде", "өнерді", "тәжірибеден",
    ]

    def test_buzylgan_tabylady(self):
        for soz in self.BUZYQ:
            with self.subTest(soz=soz):
                self.assertTrue(undestik.tekseru(soz), soz)

    def test_duris_soz_belgilenbeidi(self):
        for soz in self.DURYS:
            with self.subTest(soz=soz):
                self.assertEqual(undestik.tekseru(soz), [], soz)

    def test_tuzetilgen_nusqa_duris(self):
        (u,) = undestik.tekseru("дедлайнге")
        self.assertEqual(u.tuzetilgen, "дедлайнға")

    def test_kumandi_dauysty_tekserilmeidi(self):
        # «у» кірме сөздерде екі түрлі ұстанады — тексеруден тыс.
        self.assertEqual(undestik.tekseru("институтке"), [])

    def test_qysqa_tubir_otkizip_jiberiledi(self):
        # «да» — түбірдің өзі, қосымша емес.
        self.assertEqual(undestik.tekseru("ада"), [])


class TranslitDurystyqTest(unittest.TestCase):
    """QazLat 2021: `I ı` мен `İ i` — бөлек әріптер."""

    def test_i_nuktesiz(self):
        self.assertEqual(translit.latynga("тіл"), "tıl")

    def test_i_nukteli(self):
        self.assertEqual(translit.latynga("идея"), "ideia")

    def test_i_men_i_ajyratylady(self):
        self.assertNotEqual(translit.latynga("тіл"), translit.latynga("тил"))

    def test_bas_arip_turikshe(self):
        self.assertEqual(translit.latynga("Іле"), "Ile")     # ı → I
        self.assertEqual(translit.latynga("Идея"), "İdeia")  # i → İ

    def test_ascii_diakritikany_tusiredi(self):
        for soz in ["Әсем", "Идея", "Іле", "Ғайша", "Ңұр", "Өмір", "Шаш"]:
            with self.subTest(soz=soz):
                self.assertTrue(
                    translit.latynga(soz, ascii_qauipsiz=True).isascii(), soz
                )

    def test_hashtag_arqashan_ascii(self):
        self.assertTrue(translit.hashtag_nusqalary("Әсем тіл")["латын"].isascii())


class AuditUndestikTest(unittest.TestCase):
    def test_undestik_esepke_kiredi(self):
        r = audit.tolyq("дедлайнге үлгермедік")
        self.assertEqual(len(r.undestik), 1)

    def test_undestik_jiberuge_kedergi_emes(self):
        # Үндестік — кеңес деңгейі, қатты қате емес.
        r = audit.tolyq("дедлайнге үлгермедік")
        self.assertTrue(r.joneltuge_dayin)


class JurnalTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.jol = pathlib.Path(tempfile.mkdtemp()) / "j.jsonl"

    def _jaz(self, formula, korsetilim=None, jauap=None, laik=None):
        jurnal.jaz(
            jurnal.Jazba(
                kuni="2026-09-01",
                formula=formula,
                maqsat="jauap",
                mati_bas="сынақ",
                olshem=jurnal.Olshem(
                    korsetilim=korsetilim, jauap=jauap, laik=laik
                ),
            ),
            self.jol,
        )

    def test_bos_jurnal(self):
        self.assertEqual(jurnal.oqy(self.jol), [])
        self.assertIn("бос", jurnal.esep(self.jol))

    def test_jazu_men_oqu_ainalymy(self):
        self._jaz("Q3", 1000, 20, 50)
        (j,) = jurnal.oqy(self.jol)
        self.assertEqual(j.formula, "Q3")
        self.assertEqual(j.olshem.korsetilim, 1000)
        self.assertEqual(j.olshem.jauap, 20)

    def test_olshemsiz_jazba_esepke_kirmeidi(self):
        self._jaz("Q3")  # сан жоқ
        (q,) = jurnal.qorytu(jol=self.jol)
        self.assertEqual(q.sany, 1)
        self.assertEqual(q.olshengen, 0)
        self.assertIsNone(q.ortasha_jauap)

    def test_jauap_ulesi_eseptelinedi(self):
        self._jaz("Q3", 1000, 20, 50)
        (q,) = jurnal.qorytu(jol=self.jol)
        self.assertAlmostEqual(q.ortasha_jauap, 0.02)

    def test_az_ulgi_senimsiz_dep_belgilenedi(self):
        for _ in range(jurnal.EN_AZ_ULGI - 1):
            self._jaz("Q3", 1000, 20, 50)
        (q,) = jurnal.qorytu(jol=self.jol)
        self.assertFalse(q.senimdi)

    def test_jeterlik_ulgi_senimdi(self):
        for _ in range(jurnal.EN_AZ_ULGI):
            self._jaz("Q3", 1000, 20, 50)
        (q,) = jurnal.qorytu(jol=self.jol)
        self.assertTrue(q.senimdi)

    def test_mediana_qoldanylady_ortasha_emes(self):
        # Бір вирусты пост медиананы бұрмаламауы керек.
        for _ in range(4):
            self._jaz("Q3", 1000, 10)      # 1%
        self._jaz("Q3", 1000, 500)          # 50% — вирусты
        (q,) = jurnal.qorytu(jol=self.jol)
        self.assertAlmostEqual(q.ortasha_jauap, 0.01)

    def test_jauap_ulesi_boiynsha_rettelinedi(self):
        for _ in range(2):
            self._jaz("Q2", 1000, 5)
            self._jaz("Q3", 1000, 30)
        qorytyndy = jurnal.qorytu(jol=self.jol)
        self.assertEqual(qorytyndy[0].formula, "Q3")

    def test_korsetilimsiz_ules_eseptelmeidi(self):
        o = jurnal.Olshem(jauap=10)  # көрсетілім жоқ
        self.assertFalse(o.toly)
        self.assertIsNone(o.jauap_ulesi())

    def test_esep_az_ulgide_eskertedi(self):
        self._jaz("Q3", 1000, 20)
        self.assertIn("ҚОРЫТЫНДЫ", jurnal.esep(self.jol))


class EvalQuramTest(unittest.TestCase):
    """Әр шеберліктің eval жинағы бар әрі дұрыс құрылған ба."""

    TUBIR = pathlib.Path(__file__).resolve().parents[1]

    def test_eval_tekserushi_otedi(self):
        import subprocess

        r = subprocess.run(
            [sys.executable, str(self.TUBIR / "scripts" / "eval_tekseru.py")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_ar_skildte_eval_bar(self):
        for buma in sorted(self.TUBIR.glob("skills/*/")):
            with self.subTest(skild=buma.name):
                self.assertTrue((buma / "evals" / "evals.json").exists())


TOLY_PROFIL = """# Дауыс профилі

## Кім

Қазақша оқу қосымшасын жасаймын.

## Аудитория

Мектеп мұғалімдері.

## Регистр

- Сен/сіз: сен
- Кодты ауыстыру: шамалы

## Бағаналар

- Жұмыс: нақты сандар
- Тіл: қазақ тілі туралы байқаулар

## Айтпайтын сөздер

- инновациялық
- синергия

## Мысалдар

Интерфейсті қазақшаладым.
"""


class RegistrTabuTest(unittest.TestCase):
    """«сенім», «сенбі», «мәнсіз» деген сөздер жалған белгі бермеуі керек."""

    def test_sen_tabylady(self):
        self.assertEqual(profil.registr_tabu("Сен қалай ойлайсың?"), (2, 0))

    def test_siz_tabylady(self):
        sen, siz = profil.registr_tabu("Сіздің атыңыз кім?")
        self.assertEqual(sen, 0)
        self.assertGreater(siz, 0)

    def test_sen_bastalatyn_sozder_jalgan_belgi_bermeidi(self):
        for soz in ["Сеніммен айтам", "Сенбіде кездесеміз", "Сенімді шешім",
                    "Сенім деген осы"]:
            with self.subTest(soz=soz):
                self.assertEqual(profil.registr_tabu(soz), (0, 0), soz)

    def test_siz_jurnagy_jalgan_belgi_bermeidi(self):
        # «-сыз/-сіз» болымсыздық жұрнағы регистр белгісі емес.
        for soz in ["Мәнсіз әңгіме", "Ақшасыз қалдық", "Себепсіз күлкі"]:
            with self.subTest(soz=soz):
                self.assertEqual(profil.registr_tabu(soz), (0, 0), soz)

    def test_etistik_jalgauy_tabylady(self):
        sen, _ = profil.registr_tabu("Мұны қалай көресің?")
        self.assertEqual(sen, 1)


class ProfilOquTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.buma = pathlib.Path(tempfile.mkdtemp())

    def _jaz(self, mazmun):
        jol = self.buma / "p.md"
        profil.jaz(mazmun, jol)
        return jol

    def test_fail_joq_bolsa_none(self):
        self.assertIsNone(profil.oqy(self.buma / "joq.md"))

    def test_toltyrylgan_profil_oqylady(self):
        p = profil.oqy(self._jaz(TOLY_PROFIL))
        self.assertEqual(p.registr, "сен")
        self.assertEqual(p.kod_auystyru, "шамалы")
        self.assertEqual(p.audytoriya, "Мектеп мұғалімдері.")
        self.assertEqual(len(p.baganalar), 2)
        self.assertIn("инновациялық", p.aitpaityn_sozder)
        self.assertTrue(p.toly)

    def test_toltyrylmagan_ulgi_bos_dep_tanylady(self):
        p = profil.oqy(self._jaz(profil.ulgi()))
        self.assertFalse(p.toly)
        self.assertIn("Регистр (сен/сіз)", p.bos_orindar)

    def test_ulgideg_tusiniktemeler_tizimge_kirmeidi(self):
        p = profil.oqy(self._jaz(profil.ulgi()))
        self.assertEqual(p.baganalar, [])
        self.assertEqual(p.aitpaityn_sozder, [])

    def test_jaramsyz_registr_bos_qalady(self):
        p = profil.oqy(self._jaz(
            TOLY_PROFIL.replace("Сен/сіз: сен", "Сен/сіз: әрқалай")))
        self.assertEqual(p.registr, "")


class SaikestikTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        jol = pathlib.Path(tempfile.mkdtemp()) / "p.md"
        profil.jaz(TOLY_PROFIL, jol)
        self.p = profil.oqy(jol)

    def test_registr_aralasqany_qate(self):
        (b,) = profil.saikestik("Сен қалай ойлайсың? Сізге не керек?", self.p)
        self.assertEqual(b.turi, "регистр")
        self.assertEqual(b.dengei, "qate")

    def test_aralasu_profilsiz_de_ustalady(self):
        (b,) = profil.saikestik("Сен қалайсың? Сізге не керек?", None)
        self.assertEqual(b.dengei, "qate")

    def test_profilge_qaishy_registr_eskertu(self):
        (b,) = profil.saikestik("Сізге бір нәрсе айтайын, қараңыз.", self.p)
        self.assertEqual(b.dengei, "eskertu")

    def test_profilge_sai_matin_taza(self):
        self.assertEqual(profil.saikestik("Сен қалай ойлайсың?", self.p), [])

    def test_tyiym_salyngan_soz_tabylady(self):
        (b,) = profil.saikestik("Біздің инновациялық шешім", self.p)
        self.assertEqual(b.turi, "тыйым")

    def test_tyiym_jalgauymen_de_tabylady(self):
        # «инновациялық» → «инновациялықтан» да ұсталуы керек
        self.assertTrue(profil.saikestik("инновациялықтан бас тарттық", self.p))

    def test_profilsiz_tyiym_tekserilmeidi(self):
        self.assertEqual(profil.saikestik("Біздің инновациялық шешім", None), [])


class AuditProfilTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.jol = pathlib.Path(tempfile.mkdtemp()) / "p.md"
        profil.jaz(TOLY_PROFIL, self.jol)

    def test_profil_joly_arqyly_oqylady(self):
        r = audit.tolyq("Біздің инновациялық шешім", profil_joly=self.jol)
        self.assertTrue(r.profil_bar)
        self.assertTrue(r.profil)

    def test_profil_none_bolsa_tekserilmeidi(self):
        r = audit.tolyq("Біздің инновациялық шешім", profil=None)
        self.assertFalse(r.profil_bar)
        self.assertEqual(r.profil, [])

    def test_registr_aralasuy_jiberuge_kedergi(self):
        r = audit.tolyq("Сен қалайсың? Сізге не керек?", profil=None)
        self.assertFalse(r.joneltuge_dayin)

    def test_tyiym_jiberuge_kedergi_emes(self):
        # Тыйым — ескерту деңгейі, қатты қате емес.
        r = audit.tolyq("Біздің инновациялық шешім", profil_joly=self.jol)
        self.assertTrue(r.joneltuge_dayin)

    def test_belgi_profilsiz_de_esepte_korinedi(self):
        esep = str(audit.tolyq("Сен қалайсың? Сізге не керек?", profil=None))
        self.assertIn("регистр", esep)


if __name__ == "__main__":
    unittest.main()
