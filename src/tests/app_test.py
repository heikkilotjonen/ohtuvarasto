import unittest
import app as app_module
from app import app


class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        # Clear warehouses and reset ID counter before each test
        app_module.varastot.clear()
        app_module.next_id = 1

    def tearDown(self):
        app_module.varastot.clear()

    def test_index_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Ohtuvarasto", response.data)

    def test_index_shows_empty_message_when_no_warehouses(self):
        response = self.client.get("/")
        self.assertIn("Ei varastoja".encode("utf-8"), response.data)

    def test_create_warehouse(self):
        response = self.client.post(
            "/varastot",
            data={"nimi": "Testivarasto", "tilavuus": 100, "alku_saldo": 50},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Testivarasto", response.data)
        self.assertEqual(len(app_module.varastot), 1)

    def test_create_warehouse_with_default_name(self):
        response = self.client.post(
            "/varastot",
            data={"nimi": "", "tilavuus": 100, "alku_saldo": 0},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(app_module.varastot), 1)
        self.assertEqual(app_module.varastot[1]["nimi"], "Varasto 1")

    def test_create_warehouse_with_invalid_tilavuus_redirects(self):
        response = self.client.post(
            "/varastot",
            data={"nimi": "Testivarasto", "tilavuus": -10, "alku_saldo": 0},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(app_module.varastot), 0)

    def test_view_warehouse(self):
        self.client.post(
            "/varastot",
            data={"nimi": "Testivarasto", "tilavuus": 100, "alku_saldo": 50},
        )
        response = self.client.get("/varastot/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Testivarasto", response.data)

    def test_view_nonexistent_warehouse_redirects(self):
        response = self.client.get("/varastot/999", follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_add_to_warehouse(self):
        self.client.post(
            "/varastot",
            data={"nimi": "Testivarasto", "tilavuus": 100, "alku_saldo": 10},
        )
        response = self.client.post(
            "/varastot/1/lisaa", data={"maara": 20}, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(app_module.varastot[1]["varasto"].saldo, 30)

    def test_take_from_warehouse(self):
        self.client.post(
            "/varastot",
            data={"nimi": "Testivarasto", "tilavuus": 100, "alku_saldo": 50},
        )
        response = self.client.post(
            "/varastot/1/ota", data={"maara": 20}, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(app_module.varastot[1]["varasto"].saldo, 30)

    def test_edit_warehouse_page_loads(self):
        self.client.post(
            "/varastot",
            data={"nimi": "Testivarasto", "tilavuus": 100, "alku_saldo": 50},
        )
        response = self.client.get("/varastot/1/muokkaa")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Muokkaa", response.data)

    def test_edit_warehouse(self):
        self.client.post(
            "/varastot",
            data={"nimi": "Testivarasto", "tilavuus": 100, "alku_saldo": 50},
        )
        response = self.client.post(
            "/varastot/1/muokkaa",
            data={"nimi": "Uusi nimi", "tilavuus": 200},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(app_module.varastot[1]["nimi"], "Uusi nimi")
        self.assertAlmostEqual(app_module.varastot[1]["varasto"].tilavuus, 200)

    def test_delete_warehouse(self):
        self.client.post(
            "/varastot",
            data={"nimi": "Testivarasto", "tilavuus": 100, "alku_saldo": 50},
        )
        self.assertEqual(len(app_module.varastot), 1)
        response = self.client.post("/varastot/1/poista", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(app_module.varastot), 0)

    def test_delete_nonexistent_warehouse_redirects(self):
        response = self.client.post("/varastot/999/poista", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_add_negative_amount_does_nothing(self):
        self.client.post(
            "/varastot",
            data={"nimi": "Testivarasto", "tilavuus": 100, "alku_saldo": 50},
        )
        self.client.post("/varastot/1/lisaa", data={"maara": -10}, follow_redirects=True)
        self.assertAlmostEqual(app_module.varastot[1]["varasto"].saldo, 50)

    def test_take_negative_amount_does_nothing(self):
        self.client.post(
            "/varastot",
            data={"nimi": "Testivarasto", "tilavuus": 100, "alku_saldo": 50},
        )
        self.client.post("/varastot/1/ota", data={"maara": -10}, follow_redirects=True)
        self.assertAlmostEqual(app_module.varastot[1]["varasto"].saldo, 50)
