from flexipy.main import Flexipy


class Personalistika(Flexipy):
    def get_people(self, query=None, detail="summary", **kwargs):
        """Return people from FlexiBee evidence ``osoba``."""
        d = self.get_all_records("osoba", query, detail, **kwargs)
        return d

    def get_all_osoby(self, query=None, detail="summary", **kwargs):
        """Backward-compatible alias for :meth:`get_people`."""
        return self.get_people(query, detail, **kwargs)

    def get_person(self, id, detail="summary"):
        """Return one person by FlexiBee id or code."""
        return self.get_evidence_item(id, "osoba", detail)

    def get_osoba(self, id, detail="summary"):
        """Backward-compatible alias for :meth:`get_person`."""
        return self.get_person(id, detail)
