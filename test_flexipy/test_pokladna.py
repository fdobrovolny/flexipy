from datetime import date
from uuid import uuid4

import pytest
import requests

from flexipy import Pokladna, config


class TestPokladna:
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
        self.pokladna = Pokladna(self.conf)
        self.created_id = None

    def teardown_method(self):
        if self.created_id is not None:
            self.pokladna.delete_pokladni_doklad(self.created_id)

    def test_create_get_update_delete_pokladni_doklad(self):
        code = "FXP" + uuid4().hex[:12].upper()

        result = self.pokladna.create_pokladni_doklad(
            kod=code,
            datum_vyst=str(date.today()),
            typ_pohybu="typPohybu.vydej",
            dalsi_param={"popis": "Flexipy pokladna test"},
        )
        assert result[0] is True
        self.created_id = result[1]

        item = self.pokladna.get_pokladni_doklad_by_code(code, detail="full")
        assert item["id"] == str(self.created_id)
        assert item["kod"] == code
        assert item["popis"] == "Flexipy pokladna test"
        assert item["typPohybuK"] == "typPohybu.vydej"
        assert item["typDokl"] == "code:" + self.conf.get_typ_pokladni_pohyb()[0]
        assert item["pokladna"] == "code:" + self.conf.get_typ_pokladna()[0]
        assert item["metodaZaokrDoklK"] == "metodaZaokr.0sazba"

        update = self.pokladna.update_pokladni_doklad(
            self.created_id,
            {"popis": "Flexipy pokladna test updated"},
        )
        assert update[0] is True
        assert update[1] == self.created_id

        updated = self.pokladna.get_pokladni_doklad(self.created_id, detail="full")
        assert updated["popis"] == "Flexipy pokladna test updated"

    def test_get_cash_sum(self):
        result = self.pokladna.get_cash_sum()
        assert isinstance(result, dict)
        assert "sum" in result

    def test_get_cash_relations(self):
        result = self.pokladna.get_cash_relations()
        assert isinstance(result, dict)
        assert "relations" in result

    def test_get_cash_reports(self):
        result = self.pokladna.get_cash_reports()
        assert isinstance(result, dict)
        assert "reports" in result

    def test_get_unpaired_cash_transactions(self):
        result = self.pokladna.get_unpaired_cash_transactions()
        assert isinstance(result, list)
        for item in result:
            assert item.get("sparovano") in (False, "false", None, "")
