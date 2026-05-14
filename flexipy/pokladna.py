# -*- coding: utf-8 -*-

from .config import Config
from .main import Flexipy


class Pokladna(Flexipy):
    def __init__(self, conf=None):
        if conf is None:
            conf = Config()
        Flexipy.__init__(self, config=conf)

    def get_cash_transactions(self, query=None, detail="summary", **kwargs):
        """Return cash transactions from FlexiBee evidence ``pokladni-pohyb``."""
        return self.get_all_records("pokladni-pohyb", query, detail, **kwargs)

    def get_all_pokladni_doklady(self, query=None, detail="summary", **kwargs):
        """Backward-compatible alias for :meth:`get_cash_transactions`."""
        return self.get_cash_transactions(query, detail, **kwargs)

    def delete_cash_transaction(self, id):
        """Delete a cash transaction by FlexiBee id or code."""
        self.delete_item(id, "pokladni-pohyb")

    def delete_pokladni_doklad(self, id):
        """Backward-compatible alias for :meth:`delete_cash_transaction`."""
        self.delete_cash_transaction(id)

    def get_cash_transaction(self, id, detail="summary"):
        """Return one cash transaction by FlexiBee id or code."""
        return self.get_evidence_item(id, "pokladni-pohyb", detail)

    def get_pokladni_doklad(self, id, detail="summary"):
        """Backward-compatible alias for :meth:`get_cash_transaction`."""
        return self.get_cash_transaction(id, detail)

    def get_cash_transaction_by_code(self, code, detail="summary"):
        """Return one cash transaction by FlexiBee ``kod``."""
        return self.get_evidence_item_by_code(str(code), "pokladni-pohyb", detail)

    def get_pokladni_doklad_by_code(self, code, detail="summary"):
        """Backward-compatible alias for :meth:`get_cash_transaction_by_code`."""
        return self.get_cash_transaction_by_code(code, detail)

    def update_cash_transaction(self, id, cash_item):
        """Update a cash transaction with raw FlexiBee field values."""
        return self.update_evidence_item(id, "pokladni-pohyb", cash_item)

    def update_pokladni_doklad(self, id, pokladni_item):
        """Backward-compatible alias for :meth:`update_cash_transaction`."""
        return self.update_cash_transaction(id, pokladni_item)

    def create_cash_transaction(
        self,
        code,
        issued_on,
        movement_type=None,
        document_type=None,
        warehouse_source=False,
        cash_register_type=None,
        extra_params=None,
    ):
        """Create a cash transaction.

        ``extra_params`` is passed to FlexiBee as a raw field dictionary, so
        keys must use FlexiBee field names such as ``popis``.
        """
        if document_type is None:
            document_type = self.conf.get_typ_pokladni_pohyb()[0]
        document_type = "code:" + document_type
        if movement_type is None:
            movement_type = self.conf.get_typ_pohybu()[0]
        if cash_register_type is None:
            cash_register_type = self.conf.get_typ_pokladna()[0]
        cash_register_type = "code:" + cash_register_type
        issued_on += "+01:00"
        p_item = {
            "kod": code,
            "datVyst": issued_on,
            "typDokl": document_type,
            "typPohybuK": movement_type,
            "pokladna": cash_register_type,
            "zdrojProSkl": warehouse_source,
            "metodaZaokrDoklK": "metodaZaokr.0sazba",
            "vytvaretKorPol": False,
        }
        if extra_params is not None:
            self.validate_params(extra_params, "pokladni-pohyb")
            for key, value in extra_params.items():
                p_item[key] = value
        return self.create_evidence_item("pokladni-pohyb", p_item)

    def create_pokladni_doklad(
        self,
        kod,
        datum_vyst,
        typ_pohybu=None,
        typ_dokl=None,
        zdroj_pro_sklad=False,
        typ_pokladna=None,
        dalsi_param=None,
    ):
        """Backward-compatible alias for :meth:`create_cash_transaction`."""
        return self.create_cash_transaction(
            code=kod,
            issued_on=datum_vyst,
            movement_type=typ_pohybu,
            document_type=typ_dokl,
            warehouse_source=zdroj_pro_sklad,
            cash_register_type=typ_pokladna,
            extra_params=dalsi_param,
        )
