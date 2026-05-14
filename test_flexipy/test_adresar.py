from datetime import datetime

import pytest
import requests

from flexipy import Adresar, config


class TestAdresar:
    def setup_method(self):
        self.conf = config.TestingConfig()
        server_settings = self.conf.get_server_config()
        self.username = str(server_settings["username"])
        self.password = str(server_settings["password"])
        self.url = str(server_settings["url"])
        try:
            requests.get(
                self.url,
                auth=(self.username, self.password),
                verify=False,
                timeout=2,
            )
        except requests.exceptions.RequestException:
            pytest.skip("FlexiBee test server is not available")
        self.adresar = Adresar(self.conf)
        self.created_id = None

    def teardown_method(self):
        if self.created_id is not None:
            self.adresar.delete_adresar(self.created_id)

    def test_create_get_update_delete_adresar(self):
        code = "FX" + datetime.now().strftime("%m%d%H%M%S")

        result = self.adresar.create_adresar(
            kod=code,
            nazev="Flexipy test address",
            dalsi_param={"email": "flexipy-test@example.com", "mesto": "Praha"},
        )
        assert result[0] is True
        self.created_id = result[1]

        item = self.adresar.get_adresar_by_code(code, detail="full")
        assert item["id"] == str(self.created_id)
        assert item["kod"] == code
        assert item["nazev"] == "Flexipy test address"
        assert item["email"] == "flexipy-test@example.com"
        assert item["mesto"] == "Praha"

        update = self.adresar.update_adresar(
            self.created_id,
            {"nazev": "Flexipy test address updated"},
        )
        assert update[0] is True
        assert update[1] == self.created_id

        updated = self.adresar.get_adresar(self.created_id, detail="full")
        assert updated["nazev"] == "Flexipy test address updated"
