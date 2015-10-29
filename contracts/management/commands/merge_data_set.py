from django.core.management.base import BaseCommand
from django.conf import settings
import os
import pandas as pd
import csv


class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args) < 1:
            print("Please specify a schedule 70 file.")
            return

        schedule_70_file_name = args[0]
        merge_result_file_name = args[1] if len(args) > 1 else os.path.join(settings.BASE_DIR, 'contracts/docs/hourly_prices.csv')

        schedule_70_df = pd.read_csv(schedule_70_file_name).fillna('')

        with open(merge_result_file_name, 'a') as f:
            writer = csv.writer(f)
            csv_row_iter = schedule_70_df.iterrows()
            next(csv_row_iter)
            for _, row in csv_row_iter:
                row_values = [
                    row['SERVICE PROPOSED (e.g. Job Title/Task)'],
                    row['PRICE OFFERED TO GSA (including IFF)'],
                    None, None, None, None,
                    row['MINIMUM EDUCATION/ CERTIFICATION LEVEL'],
                    row['MINIMUM YEARS OF EXPERIENCE'],
                    row['BUSINESS SIZE'],
                    row['WORKSITE'],
                    row['VENDOR NAME'],
                    row['CONTRACT NUMBER'],
                    row['SCHEDULE'],
                    row['SIN(s) PROPOSED'],
                    row['CURRENT CONTRACT YEAR'],
                    row['CONTRACT START DATE '],
                    row['CONTRACT END DATE']
                ]
                writer.writerow(row_values)
