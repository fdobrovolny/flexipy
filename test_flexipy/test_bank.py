from flexipy import config
from flexipy import Banka
import requests
import pytest
from datetime import date
from uuid import uuid4


class TestBanka:
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
        self.banka = Banka(self.conf)
        self.created_bank_ids = []

    def teardown_method(self):
        for bank_id in self.created_bank_ids:
            self.banka.delete_bank_doklad(bank_id)

    def test_create_bank_doklad(self):
        today = str(date.today())
        code = "FXB" + uuid4().hex[:12].upper()
        bank_account = self.banka.get_bank_accounts(limit=1)[0]["kod"]
        dalsiParam = {
            "sumZklZakl": str(13689),
            "varSym": str(48152342),
            "bezPolozek": True,
        }
        result = self.banka.create_bank_doklad(
            kod=code,
            datum_vyst=today,
            bank_ucet=bank_account,
            dalsi_param=dalsiParam,
        )
        assert result[0] == True  # expected True
        id = result[1]
        self.created_bank_ids.append(id)
        bankDoklad = self.banka.get_bank_doklad(id, detail="full")
        assert bankDoklad["varSym"] == str(48152342)
        assert bankDoklad["sumZklZakl"] == "13689.0"
