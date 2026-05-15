# -*- coding: utf-8 -*-


from .config import Config
from .exceptions import FlexipyException
from .main import Flexipy


class Banka(Flexipy):
    def __init__(self, conf=None):
        if conf is None:
            conf = Config()
        Flexipy.__init__(self, config=conf)

    def create_bank_transaction(
        self,
        code,
        issued_on,
        document_type=None,
        movement_type=None,
        bank_account=None,
        extra_params=None,
    ):
        """Create a bank transaction.

        ``extra_params`` is passed to FlexiBee as a raw field dictionary, so
        keys must use FlexiBee field names such as ``varSym`` or ``sumZklZakl``.
        """
        if document_type is None:
            document_type = self.conf.get_typ_bank_dokladu()[0]
        document_type = "code:" + document_type
        if movement_type is None:
            movement_type = self.conf.get_typ_pohybu()[0]
        if bank_account is None:
            bank_account = self.conf.get_bankovni_ucty()[0]
        bank_account = "code:" + bank_account
        b_item = {
            "kod": code,
            "datVyst": issued_on,
            "typDokl": document_type,
            "typPohybuK": movement_type,
            "banka": bank_account,
        }
        if extra_params is not None:
            self.validate_params(extra_params, "banka")
            for k, v in extra_params.items():
                b_item[k] = v
        return self.create_evidence_item("banka", b_item)

    def create_bank_doklad(
        self,
        kod,
        datum_vyst,
        typ_dokl=None,
        typ_pohybu=None,
        bank_ucet=None,
        dalsi_param=None,
    ):
        """Backward-compatible alias for :meth:`create_bank_transaction`."""
        return self.create_bank_transaction(
            code=kod,
            issued_on=datum_vyst,
            document_type=typ_dokl,
            movement_type=typ_pohybu,
            bank_account=bank_ucet,
            extra_params=dalsi_param,
        )

    def get_bank_transactions(self, query=None, detail="summary", **kwargs):
        """Return bank transactions from FlexiBee evidence ``banka``."""
        d = self.get_all_records("banka", query, detail, **kwargs)
        return d

    def get_all_bank_doklady(self, query=None, detail="summary", **kwargs):
        """Backward-compatible alias for :meth:`get_bank_transactions`."""
        return self.get_bank_transactions(query, detail, **kwargs)

    def get_bank_accounts(self, query=None, detail="summary", **kwargs):
        """Return bank accounts from FlexiBee evidence ``bankovni-ucet``."""
        d = self.get_all_records("bankovni-ucet", query, detail, **kwargs)
        return d

    def get_unpaired_bank_transactions(self, **kwargs):
        """Return unpaired bank transactions."""
        return self.get_bank_transactions(
            query="sparovano is false", detail="full", **kwargs
        )

    def get_all_bankovni_ucet(self, query=None, detail="summary", **kwargs):
        """Backward-compatible alias for :meth:`get_bank_accounts`."""
        return self.get_bank_accounts(query, detail, **kwargs)

    def get_bank_account(self, id, detail="summary"):
        """Return one bank account by FlexiBee id or code."""
        return self.get_evidence_item(id, "bankovni-ucet", detail)

    def get_bankovni_ucet(self, id, detail="summary"):
        """Backward-compatible alias for :meth:`get_bank_account`."""
        return self.get_bank_account(id, detail)

    def get_bank_account_by_code(self, code, detail="summary"):
        """Return one bank account by FlexiBee ``kod``."""
        return self.get_evidence_item_by_code(str(code), "bankovni-ucet", detail)

    def get_bankovni_ucet_by_code(self, code, detail="summary"):
        """Backward-compatible alias for :meth:`get_bank_account_by_code`."""
        return self.get_bank_account_by_code(code, detail)

    def get_bank_transaction(self, id, detail="summary"):
        """Return one bank transaction by FlexiBee id or code."""
        return self.get_evidence_item(id, "banka", detail)

    def get_bank_doklad(self, id, detail="summary"):
        """Backward-compatible alias for :meth:`get_bank_transaction`."""
        return self.get_bank_transaction(id, detail)

    def get_bank_transaction_by_code(self, code, detail="summary"):
        """Return one bank transaction by FlexiBee ``kod``."""
        return self.get_evidence_item_by_code(str(code), "banka", detail)

    def get_bank_doklad_by_code(self, code, detail="summary"):
        """Backward-compatible alias for :meth:`get_bank_transaction_by_code`."""
        return self.get_bank_transaction_by_code(code, detail)

    def delete_bank_transaction(self, id):
        """Delete a bank transaction by FlexiBee id or code."""
        self.delete_item(id, "banka")

    def delete_bank_doklad(self, id):
        """Backward-compatible alias for :meth:`delete_bank_transaction`."""
        self.delete_bank_transaction(id)

    def update_bank_transaction(self, id, bank_item):
        """Update a bank transaction with raw FlexiBee field values."""
        return self.update_evidence_item(id, "banka", bank_item)

    def update_bank_doklad(self, id, bank_item):
        """Backward-compatible alias for :meth:`update_bank_transaction`."""
        return self.update_bank_transaction(id, bank_item)

    def get_bank_sum(self, query=None):
        """Return FlexiBee ``$sum`` for ``banka``."""
        return self.get_evidence_sum("banka", query)

    def get_bank_relations(self):
        """Return relation metadata for ``banka``."""
        return self.get_evidence_relations("banka")

    def get_bank_reports(self):
        """Return report metadata for ``banka``."""
        return self.get_evidence_reports("banka")

    def pair_payments(self):
        """Ask FlexiBee to automatically pair payments with invoices."""
        r = self.send_request(method="post", endUrl="banka/automaticke-parovani.json")
        if r.status_code not in (200, 201):
            raise FlexipyException("Neznama chyba.")
        else:
            return self.process_response(r)

    def do_pair_payments(self):
        """Backward-compatible alias for :meth:`pair_payments`."""
        return self.pair_payments()

    def load_online_bank_records(self):
        """Ask FlexiBee to load bank records from configured online banking.

        See https://podpora.flexibee.eu/cs/articles/4731153-nacitani-bankovnich-vypisu.
        """
        r = self.send_request(method="post", endUrl=f"banka/nacteni-vypisu-online.json")
        if r.status_code not in (200, 201):
            raise FlexipyException(f"Chyba načítání výpisů: {r.text}")
        else:
            return self.process_response(r)

    def do_load_online_bank_records(self):
        """Backward-compatible alias for :meth:`load_online_bank_records`."""
        return self.load_online_bank_records()

    def load_bank_records(self, account_id, data):
        """Upload bank statement data for one bank account.

        ``data`` is sent as-is. For Czech bank statement encodings, callers may
        need to pass bytes, for example ``data.encode("latin2")``.
        """
        r = self.send_request(
            method="post",
            endUrl=f"bankovni-ucet/{account_id}/nacteni-vypisu.json",
            payload=data,
        )
        if r.status_code not in (200, 201):
            raise FlexipyException("Neznama chyba.")
        return self.process_response(r)

    def do_load_bank_records(self, account_id, data):
        """Backward-compatible alias for :meth:`load_bank_records`."""
        return self.load_bank_records(account_id, data)

    def load_bank_records_by_code(self, account_code, data):
        """Upload bank statement data for a bank account identified by code."""
        account = self.get_bank_account_by_code(account_code)
        return self.load_bank_records(account["id"], data)

    def do_load_bank_records_by_code(self, account_code, data):
        """Backward-compatible alias for :meth:`load_bank_records_by_code`."""
        return self.load_bank_records_by_code(account_code, data)
