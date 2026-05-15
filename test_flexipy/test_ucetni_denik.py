import pytest
import requests

from flexipy import AccountingJournal, config
from flexipy.exceptions import FlexipyException


class TestAccountingJournal:
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
        self.journal = AccountingJournal(self.conf)

    def test_get_journal_entries(self):
        rows = self.journal.get_journal_entries(detail="full", limit=3)

        assert len(rows) == 3
        assert rows[0]["idUcetniDenik"]
        assert "doklad" in rows[0]
        assert "mdUcet" in rows[0]
        assert "dalUcet" in rows[0]

    def test_get_entries_for_exact_tax_account(self):
        rows = self.journal.get_entries_for_account("343021", limit=5)

        assert len(rows) == 5
        assert all(
            row["mdUcet"] == "code:343021" or row["dalUcet"] == "code:343021"
            for row in rows
        )

    def test_get_entries_for_tax_account_prefix(self):
        rows = self.journal.get_entries_for_account_prefix("343", limit=5)

        assert len(rows) == 5
        assert all(
            row["mdUcet"].startswith("code:343")
            or row["dalUcet"].startswith("code:343")
            for row in rows
        )

    def test_get_entries_for_account_validates_side(self):
        with pytest.raises(ValueError):
            self.journal.get_entries_for_account("343021", side="bad")

    def test_bad_query_raises_flexibee_error_message(self):
        with pytest.raises(FlexipyException) as exc_info:
            self.journal.get_journal_entries(query="this is bad", detail="full")

        error = exc_info.value
        assert error.status_code == 400
        assert "Špatný formát WQL dotazu" in str(error)
        assert error.response_json["winstrom"]["success"] == "false"
        assert error.url.endswith("ucetni-denik/(this%20is%20bad).json?detail=full")
