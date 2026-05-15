import json

from flexipy import (
    AccountingJournal,
    AddressBook,
    Adresar,
    Bank,
    Banka,
    CashRegister,
    Faktura,
    Invoice,
    ObratovaPredvaha,
    Pokladna,
    TrialBalance,
    UcetniDenik,
    UcetniOsnova,
    UcetniStavy,
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


def capture_split_call(client):
    captured = {}

    def split_document(evidence, id, lines):
        captured["evidence"] = evidence
        captured["id"] = id
        captured["lines"] = lines
        return True, 42, None

    client.split_document = split_document
    return captured


def test_split_issued_invoice_sends_correct_evidence():
    invoice = Invoice(FakeConfig())
    captured = capture_split_call(invoice)

    lines = [
        {"typUcOp": "code:NÁKUP ZBOŽÍ A", "sumZkl": "75.0"},
        {"typUcOp": "code:NÁKUP ZBOŽÍ B", "sumZkl": "25.0"},
    ]
    invoice.split_issued_invoice(123, lines)

    assert captured["evidence"] == "faktura-vydana"
    assert captured["id"] == 123
    assert captured["lines"] == lines


def test_split_received_invoice_sends_correct_evidence():
    invoice = Invoice(FakeConfig())
    captured = capture_split_call(invoice)

    lines = [{"typUcOp": "code:SLUŽBY", "sumZkl": "100.0"}]
    invoice.split_received_invoice("FV2023-001", lines)

    assert captured["evidence"] == "faktura-prijata"
    assert captured["id"] == "FV2023-001"
    assert captured["lines"] == lines


def test_split_bank_transaction_sends_correct_evidence():
    bank = Bank(FakeConfig())
    captured = capture_split_call(bank)

    lines = [{"typUcOp": "code:ÚROK", "sumZkl": "50.0"}]
    bank.split_bank_transaction("B-001", lines)

    assert captured["evidence"] == "banka"
    assert captured["id"] == "B-001"
    assert captured["lines"] == lines


def test_split_cash_transaction_sends_correct_evidence():
    cash_register = CashRegister(FakeConfig())
    captured = capture_split_call(cash_register)

    lines = [{"typUcOp": "code:VÝDAJE", "sumZkl": "200.0"}]
    cash_register.split_cash_transaction(999, lines)

    assert captured["evidence"] == "pokladni-pohyb"
    assert captured["id"] == 999
    assert captured["lines"] == lines


def test_split_document_generic_method_builds_payload():
    """Test that split_document builds correct JSON payload and URL."""
    from flexipy import Flexipy

    captured_request = {}

    class FakeConfigForSplit:
        def get_server_config(self):
            return {
                "url": "http://localhost:5434/c/demo/",
                "username": "user",
                "password": "pass",
                "verify": "false",
            }

    client = Flexipy(FakeConfigForSplit())

    def fake_send_request(method, endUrl, payload=""):
        captured_request["method"] = method
        captured_request["endUrl"] = endUrl
        captured_request["payload"] = payload
        import json

        return MockResponse({
            "winstrom": {
                "success": "true",
                "results": [{"id": 42}]
            }
        })

    client.send_request = fake_send_request

    lines = [
        {"typUcOp": "code:CESTOVNÉ", "sumZkl": "750.0"},
        {"typUcOp": "code:CESTOVNÉ", "sumZkl": "250.0"},
    ]
    result = client.split_document("zavazek", "123", lines)

    assert result == (True, 42, None)
    assert captured_request["method"] == "put"
    assert captured_request["endUrl"] == "zavazek/123.json"

    import json
    payload = json.loads(captured_request["payload"])
    assert payload["winstrom"]["zavazek"]["rozuctujDoklad"]["radkyRozuctovani"] == lines


class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code
        self.url = "http://test"
        self.text = json.dumps(json_data)

    def json(self):
        return self._json
