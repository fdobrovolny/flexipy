# -*- coding: utf-8 -*-

from datetime import date
from uuid import uuid4

from flexipy import Faktura
from flexipy import config
import requests
import json
import pytest


class TestFaktura:
    def setup_method(self):
        self.conf = config.TestingConfig()
        server_settings = self.conf.get_server_config()
        self.username = str(server_settings["username"])
        self.password = str(server_settings["password"])
        self.url = str(server_settings["url"])
        try:
            requests.get(
                self.url, auth=(self.username, self.password), verify=False, timeout=2
            )
        except requests.exceptions.RequestException:
            pytest.skip("FlexiBee test server is not available")
        self.faktura = Faktura(self.conf)
        self.created_invoice_ids = []

    def teardown_method(self):
        for invoice_id in self.created_invoice_ids:
            self.faktura.delete_vydana_faktura(invoice_id)

    def test_get_all_vydane_faktury(self):
        r = requests.get(
            self.url + "faktura-vydana.json",
            auth=(self.username, self.password),
            verify=False,
        )
        d = r.json()
        list_of_invoices_expected = d["winstrom"]["faktura-vydana"]
        list_of_invoices_actual = self.faktura.get_all_vydane_faktury()
        assert list_of_invoices_expected == list_of_invoices_actual

    def test_get_all_prijate_faktury(self):
        r = requests.get(
            self.url + "faktura-prijata.json",
            auth=(self.username, self.password),
            verify=False,
        )
        d = r.json()
        if len(d["winstrom"]["faktura-prijata"]) == 1:
            list_of_invoices_expected = d["winstrom"]["faktura-prijata"][0]
        else:
            list_of_invoices_expected = d["winstrom"]["faktura-prijata"]
        list_of_invoices_actual = self.faktura.get_all_prijate_faktury()
        assert list_of_invoices_expected == list_of_invoices_actual

    def test_create_vydana_faktura(self):
        code = "FXI" + uuid4().hex[:12].upper()
        expected_data = {
            "kod": code,
            "typDokl": "code:FAKTURA",
            "firma": "code:201",
            "popis": "Flexipy test invoice",
            "sumDphZakl": "0.0",
            "bezPolozek": "true",
            "varSym": "11235484",
            "zdrojProSkl": "false",
        }
        dalsi_param = {"popis": "Flexipy test invoice", "firma": "code:201"}
        result = self.faktura.create_vydana_faktura(
            kod=code,
            var_sym="11235484",
            datum_vyst=str(date.today()),
            zdroj_pro_sklad=False,
            typ_dokl=self.conf.get_typy_faktury_vydane()[0],
            dalsi_param=dalsi_param,
        )
        assert result[0] == True  # expected True
        id = result[1]
        self.created_invoice_ids.append(id)
        actualData = self.faktura.get_vydana_faktura(id, detail="full")
        assert actualData["kod"].lower() == expected_data["kod"].lower()
        assert actualData["typDokl"] == expected_data["typDokl"]
        assert actualData["firma"] == expected_data["firma"]
        assert actualData["popis"] == expected_data["popis"]
        assert actualData["sumDphZakl"] == expected_data["sumDphZakl"]

    def test_create_vydana_faktura_polozky(self):
        code = "FXI" + uuid4().hex[:12].upper()
        polozky = [
            {
                "typPolozkyK": self.conf.get_typ_polozky_vydane()[0],
                "zdrojProSkl": False,
                "nazev": "vypujceni auta",
                "cenaMj": "4815.0",
            }
        ]
        expected_data = {
            "kod": code,
            "typDokl": "code:FAKTURA",
            "firma": "code:201",
            "popis": "Flexipy test invoice",
            "varSym": "11235484",
            "zdrojProSkl": "false",
            "polozkyFaktury": polozky,
        }
        expected_polozky = [
            {
                "typPolozkyK": "typPolozky.obecny",
                "zdrojProSkl": "false",
                "nazev": "vypujceni auta",
                "cenaMj": "4815.0",
            }
        ]
        dalsi_param = {
            "popis": "Flexipy test invoice",
            "firma": "code:201",
            "typUcOp": "code:TRŽBA SLUŽBY",
        }
        result = self.faktura.create_vydana_faktura(
            kod=code,
            var_sym="11235484",
            datum_vyst=str(date.today()),
            zdroj_pro_sklad=False,
            typ_dokl=self.conf.get_typy_faktury_vydane()[0],
            dalsi_param=dalsi_param,
            polozky_faktury=polozky,
        )
        assert result[0] == True  # expected True
        id = result[1]
        self.created_invoice_ids.append(id)
        actualData = self.faktura.get_vydana_faktura(id, detail="full")
        assert actualData["kod"].lower() == expected_data["kod"].lower()
        assert actualData["typDokl"] == expected_data["typDokl"]
        assert actualData["firma"] == expected_data["firma"]
        assert actualData["popis"] == expected_data["popis"]
        actual_polozky = next(
            item
            for item in actualData["polozkyFaktury"]
            if item["nazev"] == expected_polozky[0]["nazev"]
        )
        assert actual_polozky["typPolozkyK"] == expected_polozky[0]["typPolozkyK"]
        assert actual_polozky["nazev"] == expected_polozky[0]["nazev"]
        assert actual_polozky["cenaMj"] == expected_polozky[0]["cenaMj"]

    def test_get_unpaid_issued_invoices(self):
        rows = self.faktura.get_unpaid_issued_invoices(limit=3)
        assert isinstance(rows, list)
        for row in rows:
            assert row["zbyvaUhradit"] != "0.0"

    def test_get_overdue_issued_invoices(self):
        rows = self.faktura.get_overdue_issued_invoices(limit=3)
        assert isinstance(rows, list)

    def test_get_unpaid_received_invoices(self):
        rows = self.faktura.get_unpaid_received_invoices(limit=3)
        assert isinstance(rows, list)
        for row in rows:
            assert row["zbyvaUhradit"] != "0.0"

    def test_get_overdue_received_invoices(self):
        rows = self.faktura.get_overdue_received_invoices(limit=3)
        assert isinstance(rows, list)
