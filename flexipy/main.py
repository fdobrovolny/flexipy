# -*- coding: utf-8 -*-

import json
import re
from urllib.parse import urljoin

import requests

from . import config as config_module
from .exceptions import FlexipyException


class Flexipy(object):
    DEFAULT_TIMEOUT = 30

    def __init__(self, config=None):
        """Create a client with the default config when none is provided."""
        if config is None:
            config = config_module.Config()
        self.conf = config

    def build_url(self, endUrl):
        """Build an absolute FlexiBee URL from a relative endpoint."""
        server_settings = self.conf.get_server_config()
        base_url = str(server_settings["url"]).rstrip("/") + "/"
        return urljoin(base_url, str(endUrl).lstrip("/"))

    def send_request(self, method, endUrl, payload="", params=None):
        """Send one HTTP request to the configured FlexiBee server."""
        try:
            server_settings = self.conf.get_server_config()
            username = str(server_settings["username"])
            password = str(server_settings["password"])
            timeout = float(server_settings.get("timeout", self.DEFAULT_TIMEOUT))
            if str(server_settings["verify"]) == "true":
                verify = True
            else:
                verify = False

            r = requests.request(
                method=method,
                url=self.build_url(endUrl),
                params=self._prepare_query_params(params),
                data=payload,
                auth=(username, password),
                verify=verify,
                timeout=timeout,
            )
            self.raise_for_error_response(r)
        except requests.exceptions.Timeout as e:
            raise FlexipyException("Request timeout " + str(e))
        except requests.exceptions.ConnectionError as e:
            raise FlexipyException("Connection error " + str(e))
        else:
            return r

    def raise_for_error_response(self, response):
        """Raise ``FlexipyException`` with FlexiBee error details for failures."""
        if 200 <= response.status_code < 300:
            return

        response_json = None
        try:
            response_json = response.json()
        except ValueError:
            response_json = None

        message, message_code = self.extract_error_message(response_json)
        if message is None:
            message = response.text or response.reason or "Neznama chyba."

        raise FlexipyException(
            message,
            status_code=response.status_code,
            message_code=message_code,
            response_json=response_json,
            response_text=response.text,
            url=response.url,
        )

    def extract_error_message(self, response_json):
        """Return FlexiBee's best error message and optional message code."""
        if not isinstance(response_json, dict):
            return None, None

        winstrom = response_json.get("winstrom")
        if not isinstance(winstrom, dict):
            return None, None

        message = winstrom.get("message")
        message_code = winstrom.get("message@messageCode")
        if message:
            return message, message_code

        results = winstrom.get("results") or []
        messages = []
        for result in results:
            for error in result.get("errors", []):
                if error.get("message"):
                    messages.append(error["message"])
        if messages:
            return "; ".join(messages), message_code

        return None, message_code

    def _prepare_query_params(self, params):
        """Normalize query parameters before handing them to requests."""
        if not params:
            return None

        processed = {}
        for key, value in params.items():
            if value is None or value == "":
                continue
            if isinstance(value, bool):
                processed[key] = "true" if value else "false"
            elif isinstance(value, list):
                processed[key] = value
            else:
                processed[key] = value
        return processed or None

    def _normalize_order(self, order):
        """Normalize convenient order syntax to FlexiBee order parameters."""
        if order is None:
            return None
        if isinstance(order, str):
            orders = [order]
        else:
            orders = order

        normalized = []
        for item in orders:
            if item.startswith("-"):
                normalized.append(item[1:] + "@D")
            elif item.startswith("+"):
                normalized.append(item[1:] + "@A")
            else:
                normalized.append(item)
        return normalized

    def prepare_data(self, evidence, data):
        """Wrap an evidence item in FlexiBee's ``winstrom`` JSON envelope."""
        winstrom = {"winstrom": {evidence: [data]}}
        return json.dumps(winstrom)

    def _extract_result_id(self, response_payload, evidence=None):
        """Return saved id from normal or dry-run FlexiBee write responses."""
        result = response_payload["results"][0]
        if "id" in result:
            return int(result["id"])
        if evidence is not None and "content" in result:
            content = result["content"].get(evidence)
            if isinstance(content, list) and content:
                return int(content[0]["id"])
            if isinstance(content, dict) and "id" in content:
                return int(content["id"])
        return None

    def get_all_records(
        self,
        evidence,
        query=None,
        detail="summary",
        limit=0,
        start=None,
        params=None,
        order=None,
    ):
        """Return records from a FlexiBee evidence.

        ``query`` is a raw FlexiBee filter expression. ``detail`` is passed
        through to FlexiBee, commonly ``summary``, ``id`` or ``full``. ``limit``
        and ``start`` map to FlexiBee pagination parameters. ``order`` accepts a
        field name, a list of field names, or ``-field`` for descending order.
        """
        evidence = re.sub(r"\s", "", evidence)
        request_params = {"detail": detail}
        if limit:
            request_params["limit"] = limit
        if start:
            request_params["start"] = start
        if query is None:
            endUrl = evidence + ".json"
        else:
            endUrl = evidence + "/(" + query + ").json"
        order = self._normalize_order(order)
        if order:
            request_params["order"] = order
        if params:
            request_params.update(params)
        r = self.send_request(method="get", endUrl=endUrl, params=request_params)
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
        self.raise_for_error_response(response)
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
        self.raise_for_error_response(r)

    def get_evidence_item(self, id, evidence, detail="summary", params=None):
        """Return one evidence item by FlexiBee id or code."""
        request_params = {"detail": detail}
        if params:
            request_params.update(params)
        endUrl = evidence + "/" + str(id) + ".json"
        r = self.send_request(method="get", endUrl=endUrl, params=request_params)
        dictionary = self.process_response(r, evidence=evidence)
        return dictionary

    def get_evidence_item_by_code(self, kod, evidence, detail="summary"):
        """Return one evidence item by FlexiBee ``kod``."""
        r = self.send_request(
            method="get",
            endUrl=evidence + "/(kod='" + kod + "').json",
            params={"detail": detail},
        )
        dictionary = self.process_response(r, evidence=evidence)
        if dictionary:
            return dictionary
        else:
            raise FlexipyException("Zaznam s kodem=" + str(kod) + " nebyl nalezen.")

    def create_evidence_item(self, evidence, data, dry_run=False):
        """Create one evidence item from a raw FlexiBee field dictionary."""
        data = self.prepare_data(evidence, data)
        r = self.send_request(
            method="put",
            endUrl=evidence + ".json",
            payload=data,
            params={"dry-run": True} if dry_run else None,
        )
        d = self.process_response(r)
        if d["success"] == "true":
            id = self._extract_result_id(d, evidence)
            return (True, id, None)
        else:
            e = d["results"][0]["errors"]
            error_messages = self.prepare_error_messages(e)
            return (False, None, error_messages)

    def split_document(self, evidence, id, lines, dry_run=False):
        """Rozúčtovat doklad pomocí REST API.

        ``evidence`` je název evidence (např. ``faktura-prijata``).
        ``id`` je identifikátor dokladu (FlexiBee ``id`` nebo ``kod``).
        ``lines`` je seznam slovníků, kde každý slovník reprezentuje jeden řádek
        rozúčtování s parametry jako ``typUcOp``, ``sumZkl``, ``sazbaDph``,
        ``zklMdUcet``, ``zklDalUcet``, ``clenDph`` atd.
        """
        data = {
            "winstrom": {
                evidence: {
                    "rozuctujDoklad": {
                        "radkyRozuctovani": lines
                    }
                }
            }
        }
        payload = json.dumps(data)
        r = self.send_request(
            method="put",
            endUrl=evidence + "/" + str(id) + ".json",
            payload=payload,
            params={"dry-run": True} if dry_run else None,
        )
        d = self.process_response(r)
        if d.get("success") == "true":
            returned_id = self._extract_result_id(d, evidence)
            return (True, returned_id, None)
        else:
            e = d["results"][0]["errors"]
            error_messages = self.prepare_error_messages(e)
            return (False, None, error_messages)

    def update_evidence_item(self, id, evidence, data, dry_run=False):
        """Update one evidence item with a raw FlexiBee field dictionary."""
        self.validate_params(data, evidence)
        data = self.prepare_data(evidence, data)
        r = self.send_request(
            method="put",
            endUrl=evidence + "/" + str(id) + ".json",
            payload=data,
            params={"dry-run": True} if dry_run else None,
        )
        d = self.process_response(r)
        if d["success"] == "true":
            id = self._extract_result_id(d, evidence)
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

    def get_evidence_sum(self, evidence, query=None):
        """Return FlexiBee ``$sum`` response for an evidence."""
        evidence = re.sub(r"\s", "", evidence)
        if query is None:
            end = evidence + "/$sum.json"
        else:
            end = evidence + "/(" + query + ")/$sum.json"
        r = self.send_request(method="get", endUrl=end)
        d = self.process_response(r)
        return d

    def get_evidence_relations(self, evidence):
        """Return relation metadata for an evidence."""
        evidence = re.sub(r"\s", "", evidence)
        r = self.send_request(method="get", endUrl=evidence + "/relations.json")
        return r.json()

    def get_evidence_reports(self, evidence):
        """Return report metadata for an evidence."""
        evidence = re.sub(r"\s", "", evidence)
        r = self.send_request(method="get", endUrl=evidence + "/reports.json")
        return r.json()

    def get_evidence_pdf(self, evidence, id):
        """Return PDF bytes for one printable evidence item."""
        r = self.send_request(method="get", endUrl=evidence + "/" + str(id) + ".pdf")
        self.raise_for_error_response(r)
        return r.content
