# -*- coding: utf-8 -*-


from .config import Config
from .exceptions import FlexipyException
from .main import Flexipy


class Banka(Flexipy):
    def __init__(self, conf=Config()):
        Flexipy.__init__(self, config=conf)

    def create_bank_doklad(
        self,
        kod,
        datum_vyst,
        typ_dokl=None,
        typ_pohybu=None,
        bank_ucet=None,
        dalsi_param=None,
    ):
        """Metoda vytvori novy bankovni doklad.
        :param kod: cislo dokladu
        :param dat_vyst: datum vystaveni
        :param typ_dokl: typ bankovniho dokladu moznosti jsou definovany v configu
        :param bank_ucet: ucet uvedeny v dokladu(moznosti v konfigu)
        """
        if typ_dokl == None:
            typ_dokl = self.conf.get_typ_bank_dokladu()[0]
        typ_dokl = "code:" + typ_dokl
        if typ_pohybu == None:
            typ_pohybu = self.conf.get_typ_pohybu()[0]
        if bank_ucet == None:
            bank_ucet = self.conf.get_bankovni_ucty()[0]
        bank_ucet = "code:" + bank_ucet
        b_item = {
            "kod": kod,
            "datVyst": datum_vyst,
            "typDokl": typ_dokl,
            "typPohybuK": typ_pohybu,
            "banka": bank_ucet,
        }
        if dalsi_param != None:
            self.validate_params(dalsi_param, "banka")
            for k, v in dalsi_param.iteritems():
                b_item[k] = v
        return self.create_evidence_item("banka", b_item)

    def get_all_bank_doklady(self, query=None, detail="summary", **kwargs):
        """Metoda vrati vsechny bankovni doklady z Flexibee.
        :param query: Pokud je uveden dotaz ve formatu jaky podporuje
        Flexibee(viz dokumentace), vrati vyfiltrovane zaznamy na zaklade
        dotazu.
        :param kwargs: extra arguments to get_all_records such as pagination
        """
        d = self.get_all_records("banka", query, detail, **kwargs)
        return d

    def get_all_bankovni_ucet(self, query=None, detail="summary", **kwargs):
        """
        Získá všechny záznamy bankovních účtů.

        :param query: Volitelný dotaz pro filtrování záznamů (výchozí: None).
        :param detail: Volitelná úroveň detailu pro získání (výchozí: "summary").
        :param kwargs: Volitelné klíčové argumenty.
        :return: Seznam záznamů bankovních účtů.
        """
        d = self.get_all_records("bankovni-ucet", query, detail, **kwargs)
        return d

    def get_bankovni_ucet(self, id, detail="summary"):
        return self.get_evidence_item(id, "bankovni-ucet", detail)

    def get_bankovni_ucet_by_code(self, code, detail="summary"):
        return self.get_evidence_item_by_code(str(code), "bankovni-ucet", detail)

    def get_bank_doklad(self, id, detail="summary"):
        return self.get_evidence_item(id, "banka", detail)

    def get_bank_doklad_by_code(self, code, detail="summary"):
        return self.get_evidence_item_by_code(str(code), "banka", detail)

    def delete_bank_doklad(self, id):
        self.delete_item(id, "banka")

    def update_bank_doklad(self, id, bank_item):
        """Tato metoda provede update hodnot bankovniho dokladu ve Flexibee.
        Pro ukazku pouziti viz dokuentace
        Returns :tuple skladajici se z (success, result, error_message)
        :param: id: id zaznamu ktery bude zmenen
        :param bank_item: dictionary obsahujici zmeny
        """
        return self.update_evidence_item(id, "banka", bank_item)

    def do_pair_payments(self):
        """
        Provede automaticke sparovani plateb s fakturami.
        """
        r = self.send_request(method="post", endUrl="banka/automaticke-parovani.json")
        if r.status_code not in (200, 201):
            raise FlexipyException("Neznama chyba.")
        else:
            return self.process_response(r)

    def do_load_online_bank_records(self):
        """
        Provede automaticke načtení výpisů z banky.

        :raises FlexipyException: Pokud není návratová hodnota 200, 201

        https://podpora.flexibee.eu/cs/articles/4731153-nacitani-bankovnich-vypisu
        """
        r = self.send_request(method="post", endUrl=f"banka/nacteni-vypisu-online.json")
        if r.status_code not in (200, 201):
            raise FlexipyException(f"Chyba načítání výpisů: {r.text}")
        else:
            return self.process_response(r)

    def do_load_bank_records(self, account_id, data):
        """
        Provede automaticke nacteni vypisu.

        :param account_id: Id uctu
        :param data: Data výpisu
        :return: Standrdní result dict

        :note: Můžete mít potíže s data s češtinou pokud
        jsou ve formátu str a ne bytes (ze souboru).
        Fix:
        ```python
        data = data.encode('latin2')
        ```

        :raises FlexipyException:
        """
        r = self.send_request(
            method="post",
            endUrl=f"bankovni-ucet/{account_id}/nacteni-vypisu.json",
            payload=data,
        )
        if r.status_code not in (200, 201):
            raise FlexipyException("Neznama chyba.")
        return self.process_response(r)

    def do_load_bank_records_by_code(self, account_code, data):
        """
        Provede automaticke nacteni vypisu

        :param account_code: Kód účtu
        :param data: data
        :return:
        """
        ucet = self.get_bankovni_ucet_by_code(account_code)
        return self.do_load_bank_records(ucet["id"], data)
