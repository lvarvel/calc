from django.test import TestCase
from contracts.management.commands.load_data import Command
from contracts.services.csv_contract_decoder import CSVContractDecoder
from unittest.mock import MagicMock, patch
from hourglass import settings
import os


class LoadDataTests(TestCase):
    @patch.object(CSVContractDecoder, '__init__', return_value=None)
    @patch.object(CSVContractDecoder, 'decode')
    def test_load_data_parses_correct_file(self, mocked_decode_method, mocked_init_method):
        Command().handle()
        mocked_init_method.assert_called_with(os.path.join(settings.BASE_DIR, 'contracts/docs/hourly_prices.csv'))
        self.assertTrue(mocked_decode_method.called)
