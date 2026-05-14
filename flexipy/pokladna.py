# -*- coding: utf-8 -*-

from .config import Config
from .exceptions import FlexipyException
from .main import Flexipy


class Pokladna(Flexipy):
    def __init__(self, conf=Config()):
        Flexipy.__init__(self, config=conf)

    def get_all_pokladni_doklady(self, query=None, detail="summary", **kwargs):
        """
        Metoda vrati vsechny pokladni doklady z Flexibee.

        :param query: Pokud je uveden dotaz ve formatu jaky podporuje
        Flexibee(viz dokumentace), vrati vyfiltrovane zaznamy na zaklade
        dotazu.
        :param kwargs: extra arguments to get_all_records such as pagination
        """
        d = self.get_all_records("pokladni-pohyb", query, detail, **kwargs)
        return d

    def delete_pokladni_doklad(self, id):
        """Smaze vydanou fakturu podle id.
        :param id: id faktury
        """
        self.delete_item(id, "pokladni-pohyb")

    def get_pokladni_doklad(self, id, detail="summary"):
        return self.get_evidence_item(id, "pokladni-pohyb", detail)

    def get_pokladni_doklad_by_code(self, code, detail="summary"):
        return self.get_evidence_item_by_code(str(code), "pokladni-pohyb", detail)

    def update_pokladni_doklad(self, id, pokladni_item):
        return self.update_evidence_item(id, "pokladni-pohyb", pokladni_item)

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
        if typ_dokl == None:
            typ_dokl = self.conf.get_typ_pokladni_pohyb()[0]
        typ_dokl = "code:" + typ_dokl
        if typ_pohybu == None:
            typ_pohybu = self.conf.get_typ_pohybu()[0]
        if typ_pokladna == None:
            typ_pokladna = self.conf.get_typ_pokladna()[0]
        typ_pokladna = "code:" + typ_pokladna
        datum_vyst += "+01:00"
        p_item = {
            "kod": kod,
            "datVyst": datum_vyst,
            "typDokl": typ_dokl,
            "typPohybuK": typ_pohybu,
            "pokladna": typ_pokladna,
            "zdrojProSkl": zdroj_pro_sklad,
            "metodaZaokrDoklK": "metodaZaokr.0sazba",
            "vytvaretKorPol": False,
        }
        if dalsi_param is not None:
            self.validate_params(dalsi_param, "pokladni-pohyb")
            for key, value in dalsi_param.items():
                p_item[key] = value
        return self.create_evidence_item("pokladni-pohyb", p_item)
