from flexipy import (
    AccountingJournal,
    AddressBook,
    Adresar,
    Bank,
    Banka,
    CashRegister,
    Faktura,
    Invoice,
    UcetniDenik,
)


class FakeConfig:
    def get_typy_faktury_vydane(self):
        return ["FAKTURA"]

    def get_typy_faktury_prijate(self):
        return ["PRIJATA"]

    def get_typ_bank_dokladu(self):
        return ["BANK"]

    def get_typ_pohybu(self):
        return ["typPohybu.prijem"]

    def get_bankovni_ucty(self):
        return ["BANK-ACCOUNT"]

    def get_typ_pokladni_pohyb(self):
        return ["POKLADNA"]

    def get_typ_pokladna(self):
        return ["CASH"]

    def get_server_config(self):
        return {"url": "https://example.test/c/demo/"}


def capture_created_item(client):
    captured = {}

    def validate_params(params, evidence):
        captured.setdefault("validated", []).append((params, evidence))

    def create_evidence_item(evidence, data):
        captured["evidence"] = evidence
        captured["data"] = data
        return True, 1, None

    client.validate_params = validate_params
    client.create_evidence_item = create_evidence_item
    return captured


def test_english_class_aliases_keep_existing_classes_available():
    assert Invoice is Faktura
    assert AddressBook is Adresar
    assert Bank is Banka
    assert AccountingJournal is UcetniDenik
    assert CashRegister.__name__ == "Pokladna"


def test_create_issued_invoice_uses_english_parameters_and_raw_flexibee_fields():
    invoice = Invoice(FakeConfig())
    captured = capture_created_item(invoice)

    result = invoice.create_issued_invoice(
        code="INV-1",
        variable_symbol="123",
        issued_on="2026-05-14",
        extra_params={"firma": "code:201", "popis": "Test"},
        invoice_items=[{"nazev": "Item", "cenaMj": "10.0"}],
    )

    assert result == (True, 1, None)
    assert captured["evidence"] == "faktura-vydana"
    assert captured["data"] == {
        "kod": "INV-1",
        "varSym": "123",
        "datVyst": "2026-05-14+01:00",
        "zdrojProSkl": False,
        "typDokl": "code:FAKTURA",
        "firma": "code:201",
        "popis": "Test",
        "bezPolozek": False,
        "polozkyFaktury": [{"nazev": "Item", "cenaMj": "10.0"}],
    }


def test_existing_invoice_api_still_delegates_to_same_payload():
    invoice = Faktura(FakeConfig())
    captured = capture_created_item(invoice)

    invoice.create_vydana_faktura(
        kod="INV-1",
        var_sym="123",
        datum_vyst="2026-05-14",
        dalsi_param={"firma": "code:201"},
    )

    assert captured["evidence"] == "faktura-vydana"
    assert captured["data"]["kod"] == "INV-1"
    assert captured["data"]["varSym"] == "123"
    assert captured["data"]["firma"] == "code:201"


def test_create_entry_uses_english_parameters_and_raw_flexibee_fields():
    address_book = AddressBook(FakeConfig())
    captured = capture_created_item(address_book)

    address_book.create_entry(
        code="C-1",
        name="Customer",
        extra_params={"mesto": "Praha"},
    )

    assert captured["evidence"] == "adresar"
    assert captured["data"] == {"kod": "C-1", "nazev": "Customer", "mesto": "Praha"}


def test_create_bank_transaction_keeps_raw_flexibee_fields():
    bank = Bank(FakeConfig())
    captured = capture_created_item(bank)

    bank.create_bank_transaction(
        code="B-1",
        issued_on="2026-05-14",
        extra_params={"varSym": "123"},
    )

    assert captured["evidence"] == "banka"
    assert captured["data"]["kod"] == "B-1"
    assert captured["data"]["datVyst"] == "2026-05-14"
    assert captured["data"]["varSym"] == "123"


def test_create_cash_transaction_keeps_raw_flexibee_fields():
    cash_register = CashRegister(FakeConfig())
    captured = capture_created_item(cash_register)

    cash_register.create_cash_transaction(
        code="CASH-1",
        issued_on="2026-05-14",
        extra_params={"popis": "Cash test"},
    )

    assert captured["evidence"] == "pokladni-pohyb"
    assert captured["data"]["kod"] == "CASH-1"
    assert captured["data"]["datVyst"] == "2026-05-14+01:00"
    assert captured["data"]["popis"] == "Cash test"


def test_invoice_pdf_url_has_public_english_and_legacy_names():
    invoice = Invoice(FakeConfig())

    assert (
        invoice.get_issued_invoice_pdf_url(42)
        == "https://example.test/c/demo/faktura-vydana/42.pdf"
    )
    assert invoice.get_faktura_vydana_pdf_url(42) == invoice.get_issued_invoice_pdf_url(
        42
    )
