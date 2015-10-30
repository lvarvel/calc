from contracts.models import Contract
from django.test import TestCase
from django.utils.datetime_safe import datetime
from tempfile import NamedTemporaryFile
from contracts.services.csv_contract_decoder import CSVContractDecoder


class CsvDecoderTests(TestCase):
    def setUp(self):
        self.csv_file = NamedTemporaryFile(suffix='.csv')

        self.csv_file.write(
            b'Labor Category,Year 1/base,Year 2,Year 3,Year 4,Year 5,Education,MinExpAct,Bus Size,'
            b'Location,COMPANY NAME,CONTRACT .,Schedule,SIN NUMBER,Contract Year,Begin Date,End Date\n'
        )
        self.csv_file.write(
            b'21071-Order Filler,38.22,38.99,39.77,40.56,41.37,High School,1,O,Both,"Alutiiq Global Solutions, LLC",'
            b'GS-10F-0152P,Logistics,"874-501, 874-503, 874-504, 874-505, 874-507",2,1/9/2004,1/8/2019\n')
        self.csv_file.write(
            b'Analyst/Consultant I,66.51,,,,,Bachelors,1,O,,"Enterprise Information Services, Incorporated (d.b.a.) '
            b'Eis",GS-00F-182CA,Consolidated,"C874 1, C874 7",1,,\n'
        )
        self.csv_file.write(
            b'Analyst/Consultant I,66.51,,,,,Bachelors,6 months,O,,"Enterprise Information Services, Incorporated (d.b.a.) '
            b'Eis",GS-00F-182CA,Consolidated,"C874 1, C874 7",1,,\n'
        )

        self.csv_file.flush()

    def tearDown(self):
        self.csv_file.close()

    def test_decoder_creates_data_frame_from_file(self):
        csv_decoder = CSVContractDecoder(self.csv_file.name)

        self.assertEqual(csv_decoder.data_frame['Labor Category'][0], '21071-Order Filler')
        self.assertEqual(csv_decoder.data_frame['Year 5'][0], 41.37)

    def test_decoder_returns_array_of_contracts(self):
        contracts = CSVContractDecoder(self.csv_file.name).decode()

        self.assertEqual(len(contracts), 3)
        self.assertIsInstance(contracts[0], Contract)

    def test_decoder_creates_contract_object(self):
        contracts = CSVContractDecoder(self.csv_file.name).decode()

        self.assertEqual(contracts[0].education_level, 'HS')
        self.assertEqual(contracts[0].contract_end, datetime.strptime('1/8/2019', '%m/%d/%Y').date())
        self.assertEqual(contracts[1].contract_end, None)
        self.assertEqual(contracts[1].labor_category, 'Analyst/Consultant I')

    def test_decoder_calculates_contract_years(self):
        contracts = CSVContractDecoder(self.csv_file.name).decode()

        self.assertEqual(contracts[0].hourly_rate_year1, 38.22)
        self.assertEqual(contracts[0].hourly_rate_year2, 38.99)
        self.assertEqual(contracts[1].hourly_rate_year1, 66.51)
        self.assertEqual(contracts[1].hourly_rate_year4, None)
        self.assertEqual(contracts[0].next_year_price, 39.77)
        self.assertEqual(contracts[0].second_year_price, 40.56)

    def test_decoder_handles_bad_min_exp(self):
        contracts = CSVContractDecoder(self.csv_file.name).decode()

        self.assertEqual(contracts[2].min_years_experience, 0)
