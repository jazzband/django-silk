# Create your tests here.

from django.db import transaction

from silk.profiling.profiler import silk_profile


class TestTransactionProfiling:

    @silk_profile()
    def test_transaction_atomic(self):
        with transaction.atomic():
            # Example database operations within a transaction
            pass
