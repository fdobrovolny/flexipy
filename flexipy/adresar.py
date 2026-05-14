# -*- coding: utf-8 -*-

from .config import Config
from .main import Flexipy


class Adresar(Flexipy):
    def __init__(self, conf=None):
        if conf is None:
            conf = Config()
        Flexipy.__init__(self, config=conf)

    def get_entries(self, query=None, detail="summary", **kwargs):
        """Return address-book entries from FlexiBee evidence ``adresar``."""
        return self.get_all_records("adresar", query, detail, **kwargs)

    def get_all_adresar(self, query=None, detail="summary", **kwargs):
        """Backward-compatible alias for :meth:`get_entries`."""
        return self.get_entries(query, detail, **kwargs)

    def get_entry(self, id, detail="summary"):
        """Return one address-book entry by FlexiBee id or code."""
        return self.get_evidence_item(id, "adresar", detail)

    def get_adresar(self, id, detail="summary"):
        """Backward-compatible alias for :meth:`get_entry`."""
        return self.get_entry(id, detail)

    def get_entry_by_code(self, code, detail="summary"):
        """Return one address-book entry by FlexiBee ``kod``."""
        return self.get_evidence_item_by_code(code, "adresar", detail)

    def get_adresar_by_code(self, code, detail="summary"):
        """Backward-compatible alias for :meth:`get_entry_by_code`."""
        return self.get_entry_by_code(code, detail)

    def update_entry(self, id, entry):
        """Update an address-book entry with raw FlexiBee field values."""
        return self.update_evidence_item(id, "adresar", entry)

    def update_adresar(self, id, adresar):
        """Backward-compatible alias for :meth:`update_entry`."""
        return self.update_entry(id, adresar)

    def delete_entry(self, id):
        """Delete an address-book entry by FlexiBee id or code."""
        self.delete_item(id, "adresar")

    def delete_adresar(self, id):
        """Backward-compatible alias for :meth:`delete_entry`."""
        self.delete_entry(id)

    def create_entry(self, code, name, extra_params=None):
        """Create an address-book entry.

        ``extra_params`` is passed to FlexiBee as a raw field dictionary, so
        keys must use FlexiBee field names such as ``email`` or ``mesto``.
        """
        address_item = {"kod": code, "nazev": name}
        if extra_params is not None:
            self.validate_params(extra_params, "adresar")
            for key, value in extra_params.items():
                address_item[key] = value
        return self.create_evidence_item("adresar", address_item)

    def create_adresar(self, kod, nazev, dalsi_param=None):
        """Backward-compatible alias for :meth:`create_entry`."""
        return self.create_entry(code=kod, name=nazev, extra_params=dalsi_param)

    def create_entry_bank_account(
        self, company, account_number, bank_code, extra_params=None
    ):
        """Create a bank-account relation for an address-book entry."""
        # TODO#
        return self.create_evidence_item("adresar-bankovni-ucet")

    def create_adresar_bank_ucet(
        self, firma, cislo_uctu, kod_banky, dalsi_parametry=None
    ):
        """Backward-compatible alias for :meth:`create_entry_bank_account`."""
        return self.create_entry_bank_account(
            company=firma,
            account_number=cislo_uctu,
            bank_code=kod_banky,
            extra_params=dalsi_parametry,
        )
