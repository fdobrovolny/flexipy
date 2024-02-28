from flexipy.main import Flexipy


class Personalistika(Flexipy):
    def get_all_osoby(self, query=None, detail="summary", **kwargs):
        """
        Metoda vrati vsechny osoby z Flexibee.

        :param query: Pokud je uveden dotaz ve formatu jaky podporuje
        Flexibee(viz dokumentace), vrati vyfiltrovane zaznamy na zaklade
        dotazu.
        :param detail: detail zaznamu, viz dokumentace
        :param kwargs: extra arguments to get_all_records such as pagination
        """
        d = self.get_all_records("osoba", query, detail, **kwargs)
        return d

    def get_osoba(self, id, detail="summary"):
        """
        Metoda vrati osobu z Flexibee.

        :param id: id osoby
        :param detail: detail zaznamu, viz dokumentace
        """
        return self.get_evidence_item(id, "osoba", detail)
