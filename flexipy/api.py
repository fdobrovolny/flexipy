# -*- coding: utf-8 -*-

"""
This module implements the flexipy API.

:copyright: (c) 2012 by Jakub Ječmínek.
:license: BSD, see LICENSE for more details.
"""

from .adresar import Adresar  # noqa
from .bank import Banka  # noqa
from .faktura import Faktura  # noqa
from .obratova_predvaha import ObratovaPredvaha  # noqa
from .pokladna import Pokladna  # noqa
from .ucetni_denik import UcetniDenik  # noqa
from .ucetni_osnova import UcetniOsnova  # noqa
from .ucet import Ucet  # noqa
from .ucetni_stavy import UcetniStavy  # noqa

from .main import Flexipy  # noqa

AccountingJournal = UcetniDenik
AddressBook = Adresar
AccountBalance = UcetniStavy
Bank = Banka
CashRegister = Pokladna
ChartOfAccounts = UcetniOsnova
Invoice = Faktura
TrialBalance = ObratovaPredvaha
Account = Ucet
