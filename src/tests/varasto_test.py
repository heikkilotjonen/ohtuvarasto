import unittest
from varasto import Varasto


class TestVarasto(unittest.TestCase):
    def setUp(self):
        self.varasto = Varasto(10)

    def test_konstruktori_luo_tyhjan_varaston(self):
        # https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertAlmostEqual
        self.assertAlmostEqual(self.varasto.saldo, 0)

    def test_uudella_varastolla_oikea_tilavuus(self):
        self.assertAlmostEqual(self.varasto.tilavuus, 10)

    def test_lisays_lisaa_saldoa(self):
        self.varasto.lisaa_varastoon(8)

        self.assertAlmostEqual(self.varasto.saldo, 8)

    def test_lisays_lisaa_pienentaa_vapaata_tilaa(self):
        self.varasto.lisaa_varastoon(8)

        # vapaata tilaa pitäisi vielä olla tilavuus-lisättävä määrä eli 2
        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 2)

    def test_ottaminen_palauttaa_oikean_maaran(self):
        self.varasto.lisaa_varastoon(8)

        saatu_maara = self.varasto.ota_varastosta(2)

        self.assertAlmostEqual(saatu_maara, 2)

    def test_ottaminen_lisaa_tilaa(self):
        self.varasto.lisaa_varastoon(8)

        self.varasto.ota_varastosta(2)

        # varastossa pitäisi olla tilaa 10 - 8 + 2 eli 4
        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 4)

    def test_negatiivinen_tilavuus_nollataan(self):
        v = Varasto(-5, 0)
        self.assertAlmostEqual(v.tilavuus, 0.0)

    def test_negatiivinen_alkusaldo_nollataan(self):
        v = Varasto(10, -3)
        self.assertAlmostEqual(v.saldo, 0.0)

    def test_alkusaldo_suurempi_kuin_tilavuus_tayteen(self):
        v = Varasto(10, 15)
        self.assertAlmostEqual(v.saldo, 10)

    def test_lisaa_varastoon_negatiivinen_ei_muuta_saldoa(self):
        v = Varasto(10, 5)
        v.lisaa_varastoon(-3)
        self.assertAlmostEqual(v.saldo, 5)

    def test_lisaa_varastoon_yli_mahdollisen_tayttaa_tilavuuden(self):
        v = Varasto(10, 6)
        v.lisaa_varastoon(10)   # yrittää lisätä enemmän kuin mahtuu
        self.assertAlmostEqual(v.saldo, 10)

    def test_ota_varastosta_negatiivinen_palauttaa_nolla(self):
        v = Varasto(10, 5)
        saatu = v.ota_varastosta(-2)
        self.assertAlmostEqual(saatu, 0.0)
        self.assertAlmostEqual(v.saldo, 5)

    def test_ota_varastosta_enemman_kuin_saldo_palauttaa_kaiken_ja_nollaa(self):
        v = Varasto(10, 4)
        saatu = v.ota_varastosta(6)
        self.assertAlmostEqual(saatu, 4)
        self.assertAlmostEqual(v.saldo, 0.0)

    def test_str_palauttaa_odotetun_muodon(self):
        v = Varasto(10, 3)
        s = str(v)
        self.assertIn("saldo = 3", s)
        self.assertIn("vielä tilaa 7", s)
