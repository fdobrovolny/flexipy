import pytest
import requests

from flexipy import UcetniOsnova, config


class TestUcetniOsnova:
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
        self.ucetni_osnova = UcetniOsnova(self.conf)

    def test_get_all_ucty(self):
        rows = self.ucetni_osnova.get_all_ucty(detail="summary", limit=3)

        assert len(rows) == 3
        assert rows[0]["id"]
        assert rows[0]["kod"]
        assert rows[0]["nazev"]

    def test_get_ucet_by_code_and_id(self):
        account = self.ucetni_osnova.get_ucet_by_code("010", detail="full")

        assert account["kod"] == "010"
        assert account["nazev"] == "Dlouhodobý nehmotný majetek"
        assert account["typUctuK"] == "typUctu.rozvahovy"

        same_account = self.ucetni_osnova.get_ucet(account["id"], detail="summary")
        assert same_account["id"] == account["id"]
        assert same_account["kod"] == "010"

    def test_filter_ucty_by_code_prefix(self):
        rows = self.ucetni_osnova.get_all_ucty(
            query="kod begins '01'",
            detail="summary",
            limit=5,
        )

        assert len(rows) == 5
        assert all(row["kod"].startswith("01") for row in rows)
