# -*- coding: utf-8 -*-

import json
import re

import requests

from . import config as config_module
from .exceptions import FlexipyException


class Flexipy(object):
    def __init__(self, config=None):
        """Create a client with the default config when none is provided."""
        if config is None:
            config = config_module.Config()
        self.conf = config

    def send_request(self, method, endUrl, payload=""):
        """Send one HTTP request to the configured FlexiBee server."""
        try:
            server_settings = self.conf.get_server_config()
            url = str(server_settings["url"])
            username = str(server_settings["username"])
            password = str(server_settings["password"])
            if str(server_settings["verify"]) == "true":
                verify = True
            else:
                verify = False

            r = requests.request(
                method=method,
                url=str(url) + endUrl,
                data=payload,
                auth=(username, password),
                verify=verify,
            )
            if r.status_code == 401:
                raise FlexipyException("Nemate opravneni provest tuto operaci.")
            elif r.status_code == 402:
                raise FlexipyException("Platba vyzadovana, REST API neni aktivni.")
            elif r.status_code == 403:
                raise FlexipyException(
                    "Zakazana operace. Vase licence zrejme neumoznuje tuto operaci."
                )
            elif r.status_code == 500:
                raise FlexipyException(
                    "Server error, zrejme je neco spatne se serverem na kterem je Flexibee."
                )
        except requests.exceptions.ConnectionError as e:
            raise FlexipyException("Connection error " + str(e))
        else:
            return r

    def prepare_data(self, evidence, data):
        """Wrap an evidence item in FlexiBee's ``winstrom`` JSON envelope."""
        winstrom = {"winstrom": {evidence: [data]}}
        return json.dumps(winstrom)

    def get_all_records(
        self,
        evidence,
        query=None,
        detail="summary",
        limit=0,
        start=None,
    ):
        """Return records from a FlexiBee evidence.

        ``query`` is a raw FlexiBee filter expression. ``detail`` is passed
        through to FlexiBee, commonly ``summary``, ``id`` or ``full``. ``limit``
        and ``start`` map to FlexiBee pagination parameters.
        """
        evidence = re.sub(r"\s", "", evidence)
        if query is None:
            r = self.send_request(
                method="get",
                endUrl=(
                    evidence
                    + ".json?detail="
                    + detail
                    + (f"&limit={limit}" if limit else "")
                    + (f"&start={start}" if start else "")
                ),
            )
        else:
            r = self.send_request(
                method="get",
                endUrl=(
                    evidence
                    + "/("
                    + query
                    + ").json?detail="
                    + detail
                    + (f"&limit={limit}" if limit else "")
                    + (f"&start={start}" if start else "")
                ),
            )
        return self.process_response(r, evidence, force_list=True)

    def get_evidence_property_list(self, evidence):
        """Return FlexiBee property metadata for an evidence."""
        result = {}
        r = self.send_request(method="get", endUrl=evidence + "/properties.json")
        d = r.json()
        return d["properties"]["property"]

    def prepare_error_messages(self, e):
        """Extract error messages from a FlexiBee result payload."""
        error_messages = []
        for error in e:
            error_messages.append(error["message"])
        return error_messages

    def process_response(self, response, evidence=None, force_list=False):
        """Unwrap a FlexiBee JSON response into its useful payload."""
        if evidence is None:
            d = response.json()
            dictionary = d["winstrom"]
            return dictionary
        else:
            d = response.json()
            if len(d["winstrom"][evidence]) == 1 and not force_list:
                dictionary = d["winstrom"][evidence][0]
                return dictionary
            else:
                list_of_items = d["winstrom"][evidence]
                return list_of_items

    def delete_item(self, id, evidence):
        """Delete one item from an evidence by FlexiBee id or code."""
        r = self.send_request(
            method="delete", endUrl=evidence + "/" + str(id) + ".json"
        )
        if r.status_code not in (200, 201):
            if r.status_code == 404:
                raise FlexipyException("Zaznam s id=" + str(id) + " nebyl nalezen.")
            else:
                raise FlexipyException("Neznama chyba.")

    def get_evidence_item(self, id, evidence, detail="summary"):
        """Return one evidence item by FlexiBee id or code."""
        r = self.send_request(
            method="get", endUrl=evidence + "/" + str(id) + ".json?detail=" + detail
        )
        if r.status_code not in (200, 201):
            if r.status_code == 404:
                raise FlexipyException("Zaznam s id=" + str(id) + " nebyl nalezen.")
            else:
                raise FlexipyException("Neznama chyba.")
        else:
            dictionary = self.process_response(r, evidence=evidence)
            return dictionary

    def get_evidence_item_by_code(self, kod, evidence, detail="summary"):
        """Return one evidence item by FlexiBee ``kod``."""
        r = self.send_request(
            method="get", endUrl=evidence + "/(kod='" + kod + "').json?detail=" + detail
        )
        if r.status_code not in (200, 201):
            raise FlexipyException("Neznama chyba.")
        else:
            dictionary = self.process_response(r, evidence=evidence)
            if dictionary:
                return dictionary
            else:
                raise FlexipyException("Zaznam s kodem=" + str(kod) + " nebyl nalezen.")

    def create_evidence_item(self, evidence, data):
        """Create one evidence item from a raw FlexiBee field dictionary."""
        data = self.prepare_data(evidence, data)
        r = self.send_request(method="put", endUrl=evidence + ".json", payload=data)
        d = self.process_response(r)
        if d["success"] == "true":
            id = int(d["results"][0]["id"])
            return (True, id, None)
        else:
            e = d["results"][0]["errors"]
            error_messages = self.prepare_error_messages(e)
            return (False, None, error_messages)

    def update_evidence_item(self, id, evidence, data):
        """Update one evidence item with a raw FlexiBee field dictionary."""
        data = self.prepare_data(evidence, data)
        r = self.send_request(
            method="put", endUrl=evidence + "/" + str(id) + ".json", payload=data
        )
        d = self.process_response(r)
        if d["success"] == "true":
            id = int(d["results"][0]["id"])
            return (True, id, None)
        else:
            e = d["results"][0]["errors"]
            error_messages = self.prepare_error_messages(e)
            return (False, None, error_messages)

    def validate_params(self, params, evidence):
        """Validate raw FlexiBee field names against evidence metadata."""
        template_dict = self.get_template_dict(evidence, True)
        invalid_params = ""
        for key in params:
            if key not in template_dict:
                invalid_params += key + ", "
        if len(invalid_params) > 0:
            raise FlexipyException(
                "Dalsi parametry: " + invalid_params + "nejsou validni"
            )

    def get_template_dict(self, evidence, complete=False):
        """Create an empty writable-field template for an evidence."""
        if evidence not in self.conf.get_evidence_list():
            raise ValueError(
                "evidence arg is valid only for" + str(self.conf.get_evidence_list())
            )
        property_list = self.get_evidence_property_list(evidence)
        result = {}
        if complete == False:
            for property in property_list:
                if property["isWritable"] == "true" and property["mandatory"] == "true":
                    property_name = property["propertyName"]
                    result[property_name] = ""
        else:
            for property in property_list:
                if property["isWritable"] == "true":
                    property_name = property["propertyName"]
                    result[property_name] = ""

        return result

    def get_evidence_pdf(self, evidence, id):
        """Return PDF bytes for one printable evidence item."""
        r = self.send_request(method="get", endUrl=evidence + "/" + str(id) + ".pdf")
        if r.status_code not in (200, 201):
            if r.status_code == 404:
                raise FlexipyException("Zaznam s id=" + str(id) + " nebyl nalezen.")
            else:
                raise FlexipyException("Neznama chyba.")
        else:
            return r.content
