"""fake.py - fake gateway for paython"""

import json

from decimal import Decimal
from core import Gateway

class FakeGateway(Gateway):
    """fake gateway we use for testing, does nothing just return 'success'"""
    def __init__(self):
        """docstring for __init__"""
        pass

    def charge_setup(self):
        """setup used for charges"""
        pass

    def auth(self, amount=Decimal("0.01"), credit_card=None):
        """auth a transaction"""

        return json.dumps({'result': "success", 'amount': amount, 'credit_card': credit_card})

    def settle(self):
        """settle a transaction"""
        pass

    def capture(self):
        """capture the sale"""
        pass

    def void(self):
        """void a transaction"""
        pass

    def credit(self):
        """credit the sale"""
        pass
