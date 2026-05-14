# -*- coding: utf-8 -*-

from .config import Config
from .main import Flexipy


class UcetniDenik(Flexipy):
    def __init__(self, conf=None):
        if conf is None:
            conf = Config()
        Flexipy.__init__(self, config=conf)

    def get_journal_entries(self, query=None, detail="full", **kwargs):
        """Return accounting journal records from ``ucetni-denik``."""
        return self.get_all_records("ucetni-denik", query, detail, **kwargs)

    def get_journal_entry(self, id, detail="full"):
        """Return one accounting journal record by FlexiBee id."""
        return self.get_evidence_item(id, "ucetni-denik", detail)

    def get_entries_for_account(
        self, account_code, side="both", detail="full", **kwargs
    ):
        """Return journal entries for one exact chart-of-accounts code.

        ``side`` can be ``"md"``, ``"dal"`` or ``"both"``. ``detail`` defaults
        to ``full`` because FlexiBee's summary response does not include account
        fields such as ``mdUcet`` and ``dalUcet``.
        """
        account_code = str(account_code).replace("'", "\\'")
        query = self._account_query("=", account_code, side)
        return self.get_journal_entries(query=query, detail=detail, **kwargs)

    def get_entries_for_account_prefix(
        self, account_code_prefix, side="both", detail="full", **kwargs
    ):
        """Return journal entries for accounts whose code starts with a prefix."""
        account_code_prefix = str(account_code_prefix).replace("'", "\\'")
        query = self._account_query("begins", account_code_prefix, side)
        return self.get_journal_entries(query=query, detail=detail, **kwargs)

    def _account_query(self, operator, account_code, side):
        if side not in ("both", "md", "dal"):
            raise ValueError('side must be "both", "md" or "dal"')

        if operator == "=":
            md_query = "mdUcet='code:" + account_code + "'"
            dal_query = "dalUcet='code:" + account_code + "'"
        else:
            md_query = "mdUcet.kod begins '" + account_code + "'"
            dal_query = "dalUcet.kod begins '" + account_code + "'"

        if side == "md":
            return md_query
        if side == "dal":
            return dal_query
        return "(" + md_query + " or " + dal_query + ")"
