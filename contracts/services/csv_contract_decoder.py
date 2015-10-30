from contracts.models import Contract
from django.utils.datetime_safe import datetime
import pandas as pd
import logging

log = logging.getLogger(__name__)

FEDERAL_MIN_CONTRACT_RATE = 10.10

class CSVContractDecoder():
    def __init__(self, file_name):
        self.data_frame = pd.read_csv(file_name).fillna('')

    def decode(self):

        contracts = []

        for _, row in self.data_frame.iterrows():

            if not (row['Labor Category'] and row['Contract Year'] and row['Year 1/base']):
                continue

            contract = Contract()
            contract.idv_piid = row['CONTRACT .']
            contract.labor_category = row['Labor Category'].strip().replace('\n', ' ')
            contract.vendor_name = row['COMPANY NAME']
            contract.education_level = contract.get_education_code(row['Education'])
            contract.schedule = row['Schedule']
            contract.business_size = row['Bus Size']
            contract.contract_year = row['Contract Year']
            contract.sin = row['SIN NUMBER']
            contract.hourly_rate_year1 = contract.normalize_rate(str(row['Year 1/base']))
            contract.contractor_site = row['Location']

            if row['Begin Date']:
                contract.contract_start = datetime.strptime(row['Begin Date'], '%m/%d/%Y').date()
            if row['End Date']:
                contract.contract_end = datetime.strptime(row['End Date'], '%m/%d/%Y').date()

            try:
                contract.min_years_experience = int(row['MinExpAct'])
            except:
                contract.min_years_experience = 0

            for count, rate in enumerate(row[2:6]):
                if rate:
                    setattr(contract, 'hourly_rate_year{}'.format(count + 2), contract.normalize_rate(str(rate)))

            self.__generate_contract_rate_years(row, contract)

            contracts.append(contract)

        return contracts

    def __generate_contract_rate_years(self, row, contract):
        price_fields = {
            'current_price': getattr(contract, 'hourly_rate_year{}'.format(int(row['Contract Year'])), 0)
        }

        if row['Contract Year'] < 5:
            price_fields['next_year_price'] = getattr(contract, 'hourly_rate_year{}'.format(int(row['Contract Year']) + 1), 0)
        if row['Contract Year'] < 4:
            price_fields['second_year_price'] = getattr(contract, 'hourly_rate_year{}'.format(int(row['Contract Year']) + 2), 0)

        for field, price in price_fields.items():
            if price and price >= FEDERAL_MIN_CONTRACT_RATE:
                setattr(contract, field, price)
