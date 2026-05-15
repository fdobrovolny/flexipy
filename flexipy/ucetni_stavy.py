# -*- coding: utf-8 -*-

from .config import Config
from .main import Flexipy


class UcetniStavy(Flexipy):
    def __init__(self, conf=None):
        if conf is None:
            conf = Config()
        Flexipy.__init__(self, config=conf)

    def get_account_balances(self, query=None, detail="summary", **kwargs):
        """Return account-balance records from ``stav-uctu``."""
        return self.get_all_records("stav-uctu", query, detail, **kwargs)

    def get_stavy(self, query=None, detail="summary", **kwargs):
        """Backward-compatible alias for :meth:`get_account_balances`."""
        return self.get_account_balances(query, detail, **kwargs)

    def get_account_balance(self, id, detail="summary"):
        """Return one account-balance record by FlexiBee id or code."""
        return self.get_evidence_item(id, "stav-uctu", detail)

    def get_stav(self, id, detail="summary"):
        """Backward-compatible alias for :meth:`get_account_balance`."""
        return self.get_account_balance(id, detail)
