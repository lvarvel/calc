from django.test import TestCase
from contracts.management.commands.merge_data_set import Command
from tempfile import NamedTemporaryFile
import pandas as pd


class MergeDataSetTests(TestCase):
    def setUp(self):
        self.schedule_70_file = NamedTemporaryFile(suffix=".csv")
        self.merge_result_file = NamedTemporaryFile(suffix=".csv")

        self.merge_result_file.write(b'Labor Category,Year 1/base,Year 2,Year 3,Year 4,Year 5,Education,MinExpAct,Bus Size,Location,COMPANY NAME,CONTRACT .,Schedule,SIN NUMBER,Contract Year,Begin Date,End Date\n')
        self.merge_result_file.flush()

        self.schedule_70_file.write(b'SIN(s) PROPOSED,SERVICE PROPOSED (e.g. Job Title/Task),MINIMUM EDUCATION/ CERTIFICATION LEVEL,MINIMUM YEARS OF EXPERIENCE,"UNIT OF ISSUE (e.g. Hour, Task, Sq ft)",PRICE OFFERED TO GSA (including IFF),CONTRACT NUMBER,VENDOR NAME,BUSINESS SIZE,SCHEDULE,WORKSITE,CURRENT CONTRACT YEAR,CONTRACT START DATE ,CONTRACT END DATE\n')
        self.schedule_70_file.write(b'Dash,Spell out the entire labor category,"Only use degrees spelled out as Associates, Bachelors, Masters, or Ph.D",Whole numbers only. No range. ,Hour,Price with two decimal places,Must be full contract number,Spelled out ,S or O for small or other than small,IT Schedule 70,"Customer, contractor, or both",Must be an integer from 1-5.,Month/Day/Year,Month/Day/Year\n')
        self.schedule_70_file.write(b'132-51,Product Manager,Bachelors,5,Hour,$125.44,GS-35F-376CA,"Pink Frog Interactive, Inc.",S,IT Schedule 70,Both,1,6/24/15,6/23/20\n')
        self.schedule_70_file.flush()

        Command().handle(self.schedule_70_file.name, self.merge_result_file.name)

    def tearDown(self):
        self.schedule_70_file.close()
        self.merge_result_file.close()

    def test_handle_merges_rows_correctly(self):
        data_frame = pd.read_csv(self.merge_result_file.name).fillna('')

        self.assertEqual(len(data_frame), 1)

        last_contract = data_frame.iloc([])[0]

        self.assertEqual(last_contract['Year 1/base'], '$125.44')
        self.assertEqual(last_contract['Labor Category'], 'Product Manager')
        self.assertEqual(last_contract['Year 2'], '')
        self.assertEqual(last_contract['Year 3'], '')
        self.assertEqual(last_contract['Year 4'], '')
        self.assertEqual(last_contract['Year 5'], '')
        self.assertEqual(last_contract['Education'], 'Bachelors')
        self.assertEqual(last_contract['MinExpAct'], 5)
        self.assertEqual(last_contract['Bus Size'], 'S')
        self.assertEqual(last_contract['Location'], 'Both')
        self.assertEqual(last_contract['COMPANY NAME'], 'Pink Frog Interactive, Inc.')
        self.assertEqual(last_contract['CONTRACT .'], 'GS-35F-376CA')
        self.assertEqual(last_contract['Schedule'], 'IT Schedule 70')
        self.assertEqual(last_contract['SIN NUMBER'], '132-51')
        self.assertEqual(last_contract['Contract Year'], 1)
        self.assertEqual(last_contract['Begin Date'], '6/24/15')
        self.assertEqual(last_contract['End Date'], '6/23/20')
