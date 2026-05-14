# -*- coding: utf-8 -*-

from .config import Config
from .main import Flexipy


class UcetniOsnova(Flexipy):
    def __init__(self, conf=None):
        if conf is None:
            conf = Config()
        Flexipy.__init__(self, config=conf)

    def get_all_ucty(self, query=None, detail="summary", **kwargs):
        return self.get_all_records("ucetni-osnova", query, detail, **kwargs)

    def get_ucet(self, id, detail="summary"):
        return self.get_evidence_item(id, "ucetni-osnova", detail)

    def get_ucet_by_code(self, code, detail="summary"):
        return self.get_evidence_item_by_code(str(code), "ucetni-osnova", detail)
