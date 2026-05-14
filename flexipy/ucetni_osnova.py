# -*- coding: utf-8 -*-

from .config import Config
from .main import Flexipy


class UcetniOsnova(Flexipy):
    def __init__(self, conf=None):
        if conf is None:
            conf = Config()
        Flexipy.__init__(self, config=conf)

    def get_accounts(self, query=None, detail="summary", **kwargs):
        """Return chart-of-accounts records from ``ucetni-osnova``."""
        return self.get_all_records("ucetni-osnova", query, detail, **kwargs)

    def get_all_ucty(self, query=None, detail="summary", **kwargs):
        """Backward-compatible alias for :meth:`get_accounts`."""
        return self.get_accounts(query, detail, **kwargs)

    def get_account(self, id, detail="summary"):
        """Return one chart-of-accounts record by FlexiBee id or code."""
        return self.get_evidence_item(id, "ucetni-osnova", detail)

    def get_ucet(self, id, detail="summary"):
        """Backward-compatible alias for :meth:`get_account`."""
        return self.get_account(id, detail)

    def get_account_by_code(self, code, detail="summary"):
        """Return one chart-of-accounts record by FlexiBee ``kod``."""
        return self.get_evidence_item_by_code(str(code), "ucetni-osnova", detail)

    def get_ucet_by_code(self, code, detail="summary"):
        """Backward-compatible alias for :meth:`get_account_by_code`."""
        return self.get_account_by_code(code, detail)
