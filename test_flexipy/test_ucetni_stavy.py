import pytest
import requests

from flexipy import ObratovaPredvaha, UcetniStavy, config


class TestUcetniStavy:
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
        self.ucetni_stavy = UcetniStavy(self.conf)
        self.obratova_predvaha = ObratovaPredvaha(self.conf)

    def test_get_account_balances(self):
        rows = self.ucetni_stavy.get_account_balances(detail="full", limit=3)

        assert isinstance(rows, list)
        assert len(rows) == 3
        assert "ucet" in rows[0]
        assert "pocatek" in rows[0]
        assert "zustatekMD" in rows[0]

    def test_get_account_balances_filtered(self):
        rows = self.ucetni_stavy.get_account_balances(
            query="ucet.kod begins '343'",
            detail="full",
            limit=5,
        )

        assert isinstance(rows, list)
        assert len(rows) <= 5
        assert all(row["ucet@showAs"].startswith("343") for row in rows)

    def test_get_trial_balances(self):
        rows = self.obratova_predvaha.get_trial_balances(detail="full", limit=3)

        assert isinstance(rows, list)
        assert len(rows) == 3
        assert "ucet" in rows[0]
        assert "obratMdVse" in rows[0]
        assert "obratDalVse" in rows[0]
