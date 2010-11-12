"""fake gateway for paython"""
import json

from core import Gateway

class FakeGateway(Gateway):
    """fake gateway we use for testing, does nothing just return 'success'"""
    def __init__(self):
        """docstring for __init__"""
        super(Gateway, self).__init__()

    def auth(self, amount=Decimal("0.01"), credit_card=None):
        """auth a transaction"""
        super(Gateway, self).auth(amount, credit_card)

        return json.dumps({'result': "success", 'amount': amount, 'credit_card': credit_card})

    def settle(self):
        """settle a transaction"""
        super(Gateway, self).settle()
        pass

    def capture(self):
        """capture the sale"""
        super(Gateway, self).capture()
        pass

    def void(self):
        """void a transaction"""
        super(Gateway, self).void()
        pass

    def credit(self):
        """credit the sale"""
        super(Gateway, self).credit()
        pass
