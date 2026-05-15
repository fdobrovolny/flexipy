# -*- coding: utf-8 -*-

from .config import Config
from .main import Flexipy


class ObratovaPredvaha(Flexipy):
    def __init__(self, conf=None):
        if conf is None:
            conf = Config()
        Flexipy.__init__(self, config=conf)

    def get_trial_balances(self, query=None, detail="summary", **kwargs):
        """Return trial-balance records from ``obratova-predvaha``."""
        return self.get_all_records("obratova-predvaha", query, detail, **kwargs)

    def get_predvahy(self, query=None, detail="summary", **kwargs):
        """Backward-compatible alias for :meth:`get_trial_balances`."""
        return self.get_trial_balances(query, detail, **kwargs)

    def get_trial_balance(self, id, detail="summary"):
        """Return one trial-balance record by FlexiBee id or code."""
        return self.get_evidence_item(id, "obratova-predvaha", detail)

    def get_predvaha(self, id, detail="summary"):
        """Backward-compatible alias for :meth:`get_trial_balance`."""
        return self.get_trial_balance(id, detail)
