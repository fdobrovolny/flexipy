# -*- coding: utf-8 -*-

from .config import Config
from .main import Flexipy


class Ucet(Flexipy):
    def __init__(self, conf=None):
        if conf is None:
            conf = Config()
        Flexipy.__init__(self, config=conf)

    def get_accounts(self, query=None, detail="summary", **kwargs):
        """Return account records from FlexiBee evidence ``ucet``."""
        return self.get_all_records("ucet", query, detail, **kwargs)

    def get_all_ucty(self, query=None, detail="summary", **kwargs):
        """Backward-compatible alias for :meth:`get_accounts`."""
        return self.get_accounts(query, detail, **kwargs)

    def get_account(self, id, detail="summary"):
        """Return one account record by FlexiBee id or code."""
        return self.get_evidence_item(id, "ucet", detail)

    def get_ucet(self, id, detail="summary"):
        """Backward-compatible alias for :meth:`get_account`."""
        return self.get_account(id, detail)

    def get_account_by_code(self, code, detail="summary"):
        """Return one account record by FlexiBee ``kod``."""
        return self.get_evidence_item_by_code(str(code), "ucet", detail)

    def get_ucet_by_code(self, code, detail="summary"):
        """Backward-compatible alias for :meth:`get_account_by_code`."""
        return self.get_account_by_code(code, detail)

    def create_account(self, code, name, extra_params=None, dry_run=False):
        """Create an account record.

        ``extra_params`` is passed to FlexiBee as a raw field dictionary, so
        keys must use FlexiBee field names such as ``typUctuK`` or ``druhUctuK``.
        """
        account_item = {"kod": code, "nazev": name}
        if extra_params is not None:
            for key, value in extra_params.items():
                account_item[key] = value
        return self.create_evidence_item("ucet", account_item, dry_run=dry_run)

    def create_ucet(self, kod, nazev, dalsi_param=None, dry_run=False):
        """Backward-compatible alias for :meth:`create_account`."""
        return self.create_account(
            code=kod, name=nazev, extra_params=dalsi_param, dry_run=dry_run
        )

    def update_account(self, id, account, dry_run=False):
        """Update an account record with raw FlexiBee field values."""
        return self.update_evidence_item(id, "ucet", account, dry_run=dry_run)

    def update_ucet(self, id, ucet, dry_run=False):
        """Backward-compatible alias for :meth:`update_account`."""
        return self.update_account(id, ucet, dry_run=dry_run)

    def delete_account(self, id):
        """Delete an account record by FlexiBee id or code."""
        self.delete_item(id, "ucet")

    def delete_ucet(self, id):
        """Backward-compatible alias for :meth:`delete_account`."""
        self.delete_account(id)
