from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings
from contracts.models import Contract
import os
import logging
from contracts.services.csv_contract_decoder import CSVContractDecoder

class Command(BaseCommand):
    def handle(self, *args, **options):
        log = logging.getLogger(__name__)

        log.info("Begin load_data task")

        log.info("Deleting existing contract records")
        Contract.objects.all().delete()

        contracts = CSVContractDecoder(os.path.join(settings.BASE_DIR, 'contracts/docs/hourly_prices.csv')).decode()

        log.info("Inserting records")
        Contract.objects.bulk_create(contracts)

        log.info("Updating search index")
        call_command('update_search_field', Contract._meta.app_label, Contract._meta.model_name)

        log.info("End load_data task")
