"""lib/ модульдерінің тесттері. Сыртқы тәуелділік жоқ, unittest қана."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib import emle, kalka, translit, url_parser, maquldau, jariyalau, audit


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


if __name__ == "__main__":
    unittest.main()
