# -*- coding: utf-8 -*-

from .config import Config
from .main import Flexipy


class Faktura(Flexipy):
    def __init__(self, conf=None):
        if conf is None:
            conf = Config()
        Flexipy.__init__(self, config=conf)

    def get_issued_invoices(self, query=None, detail="summary", **kwargs):
        """Return issued invoices from FlexiBee evidence ``faktura-vydana``."""
        return self.get_all_records("faktura-vydana", query, detail, **kwargs)

    def get_all_vydane_faktury(self, query=None, detail="summary", **kwargs):
        """Backward-compatible alias for :meth:`get_issued_invoices`."""
        return self.get_issued_invoices(query, detail, **kwargs)

    def get_received_invoices(self, query=None, detail="summary", **kwargs):
        """Return received invoices from FlexiBee evidence ``faktura-prijata``."""
        return self.get_all_records("faktura-prijata", query, detail, **kwargs)

    def get_all_prijate_faktury(self, query=None, detail="summary", **kwargs):
        """Backward-compatible alias for :meth:`get_received_invoices`."""
        return self.get_received_invoices(query, detail, **kwargs)

    def create_issued_invoice(
        self,
        code,
        variable_symbol,
        issued_on,
        warehouse_source=False,
        document_type=None,
        extra_params=None,
        invoice_items=None,
    ):
        """Create an issued invoice.

        ``extra_params`` and ``invoice_items`` are passed to FlexiBee as raw
        field dictionaries, so their keys must use FlexiBee field names such as
        ``firma``, ``popis``, ``nazev`` or ``cenaMj``.
        """
        if document_type is None:
            document_type = self.conf.get_typy_faktury_vydane()[0]
        document_type = "code:" + document_type
        issued_on += "+01:00"
        invoice = {
            "kod": code,
            "varSym": variable_symbol,
            "datVyst": issued_on,
            "zdrojProSkl": warehouse_source,
            "typDokl": document_type,
        }
        if extra_params is not None:
            self.validate_params(extra_params, "faktura-vydana")
            for k, v in extra_params.items():
                invoice[k] = v
        if invoice_items is not None:
            invoice["bezPolozek"] = False
            inv_items = []
            for it in invoice_items:
                self.validate_params(it, "faktura-vydana-polozka")
                inv_items.append(it)
            invoice["polozkyFaktury"] = inv_items
        return self.create_evidence_item("faktura-vydana", invoice)

    def create_vydana_faktura(
        self,
        kod,
        var_sym,
        datum_vyst,
        zdroj_pro_sklad=False,
        typ_dokl=None,
        dalsi_param=None,
        polozky_faktury=None,
    ):
        """Backward-compatible alias for :meth:`create_issued_invoice`."""
        return self.create_issued_invoice(
            code=kod,
            variable_symbol=var_sym,
            issued_on=datum_vyst,
            warehouse_source=zdroj_pro_sklad,
            document_type=typ_dokl,
            extra_params=dalsi_param,
            invoice_items=polozky_faktury,
        )

    def create_received_invoice(
        self,
        code,
        variable_symbol,
        received_number,
        due_on,
        issued_on,
        warehouse_source=False,
        document_type=None,
        extra_params=None,
        invoice_items=None,
    ):
        """Create a received invoice.

        ``extra_params`` and ``invoice_items`` are passed to FlexiBee as raw
        field dictionaries, so their keys must use FlexiBee field names.
        """
        if document_type is None:
            document_type = self.conf.get_typy_faktury_prijate()[0]
        document_type = "code:" + document_type
        due_on += "+01:00"
        issued_on += "+01:00"
        invoice = {
            "datSplat": due_on,
            "kod": code,
            "zdrojProSkl": warehouse_source,
            "datVyst": issued_on,
            "varSym": variable_symbol,
            "cisDosle": received_number,
            "typDokl": document_type,
        }
        if extra_params is not None:
            self.validate_params(extra_params, "faktura-prijata")
            for k, v in extra_params.items():
                invoice[k] = v
        if invoice_items is not None:
            invoice["bezPolozek"] = False
            inv_items = []
            for it in invoice_items:
                self.validate_params(it, "faktura-prijata-polozka")
                inv_items.append(it)
            invoice["polozkyFaktury"] = inv_items
        return self.create_evidence_item("faktura-prijata", invoice)

    def create_prijata_faktura(
        self,
        kod,
        var_sym,
        cislo_dosle,
        datum_splat,
        datum_vyst,
        zdroj_pro_sklad=False,
        typ_dokl=None,
        dalsi_param=None,
        polozky_faktury=None,
    ):
        """Backward-compatible alias for :meth:`create_received_invoice`."""
        return self.create_received_invoice(
            code=kod,
            variable_symbol=var_sym,
            received_number=cislo_dosle,
            due_on=datum_splat,
            issued_on=datum_vyst,
            warehouse_source=zdroj_pro_sklad,
            document_type=typ_dokl,
            extra_params=dalsi_param,
            invoice_items=polozky_faktury,
        )

    def update_issued_invoice(self, id, invoice):
        """Update an issued invoice with raw FlexiBee field values."""
        return self.update_evidence_item(id, "faktura-vydana", invoice)

    def update_vydana_faktura(self, id, invoice):
        """Backward-compatible alias for :meth:`update_issued_invoice`."""
        return self.update_issued_invoice(id, invoice)

    def update_received_invoice(self, id, invoice):
        """Update a received invoice with raw FlexiBee field values."""
        return self.update_evidence_item(id, "faktura-prijata", invoice)

    def update_prijata_faktura(self, id, invoice):
        """Backward-compatible alias for :meth:`update_received_invoice`."""
        return self.update_received_invoice(id, invoice)

    def delete_issued_invoice(self, id):
        """Delete an issued invoice by FlexiBee id or code."""
        self.delete_item(id, "faktura-vydana")

    def delete_vydana_faktura(self, id):
        """Backward-compatible alias for :meth:`delete_issued_invoice`."""
        self.delete_issued_invoice(id)

    def delete_received_invoice(self, id):
        """Delete a received invoice by FlexiBee id or code."""
        self.delete_item(id, "faktura-prijata")

    def delete_prijata_faktura(self, id):
        """Backward-compatible alias for :meth:`delete_received_invoice`."""
        self.delete_received_invoice(id)

    def get_issued_invoice(self, id, detail="summary"):
        """Return one issued invoice by FlexiBee id or code."""
        return self.get_evidence_item(id, "faktura-vydana", detail)

    def get_vydana_faktura(self, id, detail="summary"):
        """Backward-compatible alias for :meth:`get_issued_invoice`."""
        return self.get_issued_invoice(id, detail)

    def get_issued_invoice_by_code(self, code, detail="summary"):
        """Return one issued invoice by FlexiBee ``kod``."""
        return self.get_evidence_item_by_code(code, "faktura-vydana", detail)

    def get_vydana_faktura_by_code(self, code, detail="summary"):
        """Backward-compatible alias for :meth:`get_issued_invoice_by_code`."""
        return self.get_issued_invoice_by_code(code, detail)

    def get_received_invoice(self, id, detail="summary"):
        """Return one received invoice by FlexiBee id or code."""
        return self.get_evidence_item(id, "faktura-prijata", detail)

    def get_prijata_faktura(self, id, detail="summary"):
        """Backward-compatible alias for :meth:`get_received_invoice`."""
        return self.get_received_invoice(id, detail)

    def get_received_invoice_by_code(self, code, detail="summary"):
        """Return one received invoice by FlexiBee ``kod``."""
        return self.get_evidence_item_by_code(code, "faktura-prijata", detail)

    def get_prijata_faktura_by_code(self, code, detail="summary"):
        """Backward-compatible alias for :meth:`get_received_invoice_by_code`."""
        return self.get_received_invoice_by_code(code, detail)

    def __get_faktura_pdf_url(self, faktura_typ, id):
        server_settings = self.conf.get_server_config()
        url = str(server_settings["url"])
        return url + faktura_typ + "/" + str(id) + ".pdf"

    def get_invoice_pdf_url(self, invoice_type, id):
        """Return the PDF URL for a raw FlexiBee invoice evidence name."""
        return self.__get_faktura_pdf_url(invoice_type, id)

    def get_faktura_pdf_url(self, faktura_typ, id):
        """Backward-compatible alias for :meth:`get_invoice_pdf_url`."""
        return self.get_invoice_pdf_url(faktura_typ, id)

    def get_issued_invoice_pdf_url(self, id):
        """Return the PDF URL for an issued invoice."""
        return self.get_invoice_pdf_url("faktura-vydana", id)

    def get_faktura_vydana_pdf_url(self, id):
        """Backward-compatible alias for :meth:`get_issued_invoice_pdf_url`."""
        return self.get_issued_invoice_pdf_url(id)

    def get_received_invoice_pdf_url(self, id):
        """Return the PDF URL for a received invoice."""
        return self.get_invoice_pdf_url("faktura-prijata", id)

    def get_faktura_prijata_pdf_url(self, id):
        """Backward-compatible alias for :meth:`get_received_invoice_pdf_url`."""
        return self.get_received_invoice_pdf_url(id)

    def get_issued_invoice_pdf(self, id):
        """Return issued invoice PDF bytes."""
        return self.get_evidence_pdf("faktura-vydana", id)

    def get_faktura_vydana_pdf(self, id):
        """Backward-compatible alias for :meth:`get_issued_invoice_pdf`."""
        return self.get_issued_invoice_pdf(id)
