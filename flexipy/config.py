# -*- coding: utf-8 -*-

"""Configuration helpers for FlexiBee connection and evidence defaults."""

import codecs
import os
import pathlib
from configparser import ConfigParser, NoSectionError
from importlib import resources


class Config(object):
    """Read Flexipy configuration from package files, paths, and environment."""

    def __init__(self, config_name=None):
        if config_name is None:
            config_name = os.environ.get("FLEXIPY_CONF", "flexipy/flexipy.conf")
        self.conf = ConfigParser()
        filename = self._resolve_config_path(config_name)
        # Open the file with the correct encoding
        try:
            with codecs.open(filename, "r", encoding="utf-8") as f:
                self.conf.read_file(f)
        except IOError:
            raise ValueError(
                "Konfiguracni soubor "
                + config_name
                + " neexistuje nebo jste uvedli spatnou cestu."
            )

        if os.environ.get("FLEXIPY_USERNAME", None) is not None:
            self.conf.set("server", "username", os.environ.get("FLEXIPY_USERNAME"))
        if os.environ.get("FLEXIPY_PASSWORD", None) is not None:
            self.conf.set("server", "password", os.environ.get("FLEXIPY_PASSWORD"))
        if os.environ.get("FLEXIPY_HOST", None) is not None:
            self.conf.set("server", "host", os.environ.get("FLEXIPY_HOST"))
        if os.environ.get("FLEXIPY_FIRMA", None) is not None:
            self.conf.set("server", "firma", os.environ.get("FLEXIPY_FIRMA"))
        if os.environ.get("FLEXIPY_PROTOCOL", None) in ["http", "https"]:
            self.conf.set("server", "protocol", os.environ.get("FLEXIPY_PROTOCOL"))
        if os.environ.get("FLEXIPY_SSL_VERIFY", None) in ["true", "false"]:
            self.conf.set("server", "verify", os.environ.get("FLEXIPY_SSL_VERIFY"))
        if os.environ.get("FLEXIPY_URL", None) is not None:
            self.conf.set("server", "url", os.environ.get("FLEXIPY_URL"))

    def _resolve_config_path(self, config_name):
        path = pathlib.Path(config_name)
        if path.is_absolute() or path.exists():
            return str(path)

        package_prefix = "flexipy/"
        if config_name.startswith(package_prefix):
            resource_name = config_name[len(package_prefix) :]
            resource_path = resources.files("flexipy").joinpath(resource_name)
            if resource_path.is_file():
                return str(resource_path)

        return config_name

    def get_section_list(self, section_name):
        """Return all values from one config section as a list."""
        result_list = []
        try:
            section_content = self.conf.items(section_name)
            for key, val in section_content:
                result_list.append(val)
        except NoSectionError:
            raise ValueError("Config file neobsahuje sekci " + section_name)
        return result_list

    def get_server_config(self):
        """Return server connection settings as a dictionary."""
        result = {}
        try:
            section_content = self.conf.items("server")
            for key, val in section_content:
                result[key] = val
        except NoSectionError:
            raise ValueError("Config file neobsahuje sekci server")
        return result

    def get_evidence_list(self):
        return self.get_section_list("evidence")

    def get_typy_faktury_prijate(self):
        return self.get_section_list("typ_faktury_prijate")

    def get_received_invoice_types(self):
        return self.get_typy_faktury_prijate()

    def get_typy_faktury_vydane(self):
        return self.get_section_list("typ_faktury_vydane")

    def get_issued_invoice_types(self):
        return self.get_typy_faktury_vydane()

    def get_typ_bank_dokladu(self):
        return self.get_section_list("typ_bank_dokladu")

    def get_bank_transaction_types(self):
        return self.get_typ_bank_dokladu()

    def get_typ_pohybu(self):
        return self.get_section_list("typ_pohybu")

    def get_movement_types(self):
        return self.get_typ_pohybu()

    def get_bankovni_ucty(self):
        return self.get_section_list("bankovni_ucty")

    def get_bank_accounts(self):
        return self.get_bankovni_ucty()

    def get_typ_polozky_vydane(self):
        return self.get_section_list("typ_polozky_vydane")

    def get_issued_item_types(self):
        return self.get_typ_polozky_vydane()

    def get_typ_ucetni_operace(self):
        return self.get_section_list("typ_ucetni_operace")

    def get_accounting_operation_types(self):
        return self.get_typ_ucetni_operace()

    def get_typ_pokladni_pohyb(self):
        return self.get_section_list("typ_pokladni_pohyb")

    def get_cash_transaction_types(self):
        return self.get_typ_pokladni_pohyb()

    def get_typ_pokladna(self):
        return self.get_section_list("typ_pokladna")

    def get_cash_register_types(self):
        return self.get_typ_pokladna()


class TestingConfig(Config):
    """Config using the bundled test FlexiBee settings."""

    def __init__(self):
        Config.__init__(self, config_name="flexipy/test_flexipy.conf")


class DemoConfig(Config):
    """Config using the bundled public demo FlexiBee settings."""

    def __init__(self):
        Config.__init__(self, config_name="flexipy/demo_flexibee.conf")
