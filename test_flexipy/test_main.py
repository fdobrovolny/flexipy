# -*- coding: utf-8 -*-

from datetime import date
from uuid import uuid4

from flexipy.main import Flexipy
from flexipy import config
from flexipy import Faktura
from flexipy.exceptions import FlexipyException
import requests
import pytest
import json


class TestFlexipy:
    def setup_method(self):
        # use testing config
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
        self.flexipy = Flexipy(self.conf)
        self.faktura = Faktura(self.conf)
        self.created_invoice_ids = []
        self.test_codes = ["FXM" + uuid4().hex[:12].upper() for _ in range(3)]
        self.spec_sym = str(int(uuid4().hex[:8], 16))
        # create some items in flexibee
        result = self.faktura.create_vydana_faktura(
            kod=self.test_codes[0],
            var_sym="11235484",
            datum_vyst=str(date.today()),
            zdroj_pro_sklad=False,
        )
        if result[0] is not True:
            self.teardown_method()
        assert result[0] is True
        self.created_invoice_ids.append(result[1])
        dalsiParams = {"specSym": self.spec_sym}
        # tyto dve jsou pro testovani get all records
        result = self.faktura.create_vydana_faktura(
            kod=self.test_codes[1],
            var_sym="11235494",
            datum_vyst=str(date.today()),
            zdroj_pro_sklad=False,
            dalsi_param=dalsiParams,
        )
        if result[0] is not True:
            self.teardown_method()
        assert result[0] is True
        self.created_invoice_ids.append(result[1])
        result = self.faktura.create_vydana_faktura(
            kod=self.test_codes[2],
            var_sym="11235495",
            datum_vyst=str(date.today()),
            zdroj_pro_sklad=False,
            dalsi_param=dalsiParams,
        )
        if result[0] is not True:
            self.teardown_method()
        assert result[0] is True
        self.created_invoice_ids.append(result[1])

    def teardown_method(self):
        if not hasattr(self, "faktura"):
            return
        for invoice_id in self.created_invoice_ids:
            self.faktura.delete_vydana_faktura(invoice_id)

    def test_validate_item(self):
        invalid_params = {"doprava": "", "duzpaPuv": "", "zaveTxt": ""}
        pytest.raises(
            FlexipyException,
            self.flexipy.validate_params,
            invalid_params,
            "faktura-vydana",
        )

    def test_get_template_dict(self):
        expected_result = {"kod": "", "nazev": ""}
        assert expected_result == self.flexipy.get_template_dict("adresar")

    def test_send_request(self):
        expected_resp = requests.get(
            url=self.url + "faktura-vydana.json",
            auth=(self.username, self.password),
            verify=False,
        )
        actual_resp = self.flexipy.send_request(
            method="get", endUrl="faktura-vydana.json"
        )
        assert expected_resp.status_code == actual_resp.status_code
        assert expected_resp.json() == actual_resp.json()

    def test_prepare_date(self):
        data = {"kod": "inv1", "nazev": "mojeFaktura"}
        expected_result = json.dumps({"winstrom": {"faktura-vydana": [data]}})
        actual_result = self.flexipy.prepare_data("faktura-vydana", data)
        assert expected_result == actual_result

    def test_get_all_records_without_query(self):
        r = requests.get(
            self.url + "faktura-vydana.json",
            auth=(self.username, self.password),
            verify=False,
        )
        expected_result = r.json()["winstrom"]["faktura-vydana"]
        actual_result = self.flexipy.get_all_records("faktura-vydana")
        assert expected_result == actual_result

    def test_get_all_records_with_query(self):
        # get all records with the unique specSym created in setup_method
        url = self.url + 'faktura-vydana/(specSym="' + self.spec_sym + '").json'
        r = requests.get(url=url, auth=(self.username, self.password), verify=False)
        expected_result = r.json()["winstrom"]["faktura-vydana"]
        actual_result = self.flexipy.get_all_records(
            "faktura-vydana", query="specSym='" + self.spec_sym + "'"
        )
        assert len(expected_result) == len(actual_result)
        assert expected_result == actual_result

    def test_get_evidence_property_list(self):
        pass
