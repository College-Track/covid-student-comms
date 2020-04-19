from salesforce_reporting import Connection, ReportParser
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import helpers
import os
import numpy as np
from reportforce import Reportforce
from gspread_pandas import Spread, Client
from dotenv import load_dotenv


SF_PASS = os.environ.get("SF_PASS")
SF_TOKEN = os.environ.get("SF_TOKEN")
SF_USERNAME = os.environ.get("SF_USERNAME")

sf = Reportforce(username=SF_USERNAME, password=SF_PASS, security_token=SF_TOKEN)


class SalesforceReport:
    def __init__(self, file_number, report_id, report_filter_column, report_name):
        self.report_name = report_name
        self.file_numer = file_number
        self.report_id = report_id
        self.report_filter_column = report_filter_column
        self.salesforce_df = None
        self.df = None

        self.in_file = "sf_output_file" + str(file_number) + ".csv"
        self.summary_file = "process_data_file" + str(file_number) + ".pkl"

        self.in_file_location = Path.cwd() / "data" / "raw" / self.in_file
        self.summary_file_location = Path.cwd() / "data" / "raw" / self.summary_file

    def read_from_salesforce(self, sf):
        self.salesforce_df = sf.get_report(
            self.report_id, id_column=self.report_filter_column
        )

    def write_csv(self, index=False):
        self.salesforce_df.to_csv(self.in_file_location, index=index)

    def read_csv(self):
        self.df = pd.read_csv(self.in_file_location)

    def write_pkl(self):
        self.df.to_pickle(sellf.summary_file_location)


files_prep = [
    {
        "name": "incoming_sms",
        "id": "00O1M0000077bWiUAI",
        "id_column": "Incoming SMS: ID",
    },
    #     {
    #         "name": "outgoing_sms",
    #         "id": "00O1M0000077bWTUAY",
    #         "id_column": "SMS History: Record number"
    #     },
]


def setup_classes(file_prep):
    _files = {}
    for i in range(len(files_prep)):
        file_number = i + 1

        file_title = files_prep[i]["name"]

        _files[file_title] = SalesforceReport(
            file_number,
            files_prep[i]["id"],
            files_prep[i]["id_column"],
            files_prep[i]["name"],
        )
    return _files


def load_from_salesforce(files_prep, files):
    for i in range(len(files_prep)):
        file_title = files_prep[i]["name"]
        files[file_title].read_from_salesforce(sf)
        files[file_title].write_csv()


def read_from_csv(files_prep, files):
    for i in range(len(files_prep)):
        file_title = files_prep[i]["name"]
        files[file_title].read_csv()


files = setup_classes(files_prep)

load_from_salesforce(files_prep, files)

read_from_csv(files_prep, files)


# One report needs to be loaded from Google Sheets

activities_sheet = Spread("1r3YGO2PMz7tVu3duCN1stQG_phFFKOjW0KZO9XKgoP8")
activities_sheet.open_sheet(0)
activities_df = activities_sheet.sheet_to_df()


# Survey Reports are also in Google Sheets


print(files["incoming_sms"].df)
