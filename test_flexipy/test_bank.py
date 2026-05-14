from flexipy import config
from flexipy import Banka
import requests
import pytest
from datetime import date


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

    def test_create_bank_doklad(self):
        today = str(date.today())
        dalsiParam = {
            "sumZklZakl": str(13689),
            "varSym": str(48152342),
            "bezPolozek": True,
        }
        result = self.banka.create_bank_doklad(
            kod="bank12", datum_vyst=today, dalsi_param=dalsiParam
        )
        assert result[0] == True  # expected True
        id = result[1]
        bankDoklad = self.banka.get_bank_doklad(id, detail="full")
        assert bankDoklad["varSym"] == str(48152342)
        assert bankDoklad["sumZklZakl"] == "13689.0"
        self.banka.delete_bank_doklad(id)
