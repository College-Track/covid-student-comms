import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import helpers
import os
import numpy as np
from reportforce import Reportforce
from gspread_pandas import Spread, Client


class SalesforceReport:
    def __init__(
        self,
        file_number,
        report_id,
        report_filter_column,
        report_name,
        date_column,
        summary_column_name,
        student_id_column,
    ):
        self.report_name = report_name
        self.file_numer = file_number
        self.report_id = report_id
        self.report_filter_column = report_filter_column
        self.salesforce_df = None
        self.df = None
        self.date_column = date_column
        self.summary_column_name = summary_column_name
        self.student_id_column = student_id_column

        self.in_file = "sf_output_file_" + self.report_name + ".csv"
        self.summary_file = "process_data_file_" + self.report_name + ".pkl"

        self.in_file_location = Path.cwd() / "data" / "raw" / self.in_file
        self.summary_file_location = Path.cwd() / "data" / "raw" / self.summary_file

        self.seven_day_summary = None
        self.thirty_day_summary = None
        self.all_time_summary = None

    def bypass_csv(self):
        self.df = self.salesforce_df

    def read_from_salesforce(self, sf):
        self.salesforce_df = sf.get_report(
            self.report_id, id_column=self.report_filter_column
        )

    def write_csv(self, index=False):
        self.salesforce_df.to_csv(self.in_file_location, index=index)

    def read_csv(self):
        self.df = pd.read_csv(self.in_file_location)

    def write_pkl(self):
        self.df.to_pickle(self.summary_file_location)

    def convert_date_column(self):
        self.df.loc[:, self.date_column] = pd.to_datetime(self.df[self.date_column])
        if self.date_column != "Date":
            self.df.rename(columns={self.date_column: "Date"}, inplace=True)

    def create_summary(self, day_limit=None, sum_type="count"):
        if day_limit == 30:
            _df = self.df[
                self.df.Date.dt.date
                >= (datetime.now().date() - timedelta(days=day_limit))
            ]
        elif day_limit == 7:
            last_week_num = int(datetime.now().strftime("%U")) - 1
            if last_week_num < 10:
                last_week_num = "0" + str(last_week_num)
            else:
                last_week_num = str(last_week_num)

            _df = self.df[self.df.Date.dt.strftime("%U") == last_week_num]
        else:
            _df = self.df.copy()

        if sum_type == "count":
            _series = _df.groupby(self.student_id_column).size()
        elif sum_type == "sum":
            _series = _df.groupby(self.student_id_column).sum()

        if day_limit:
            _series.name = self.summary_column_name + "_" + str(day_limit) + "_days"
        else:
            _series.name = self.summary_column_name
        _series.index.names = ["18 Digit ID"]

        if isinstance(_series, pd.DataFrame):
            _series = _series.reset_index()

        else:
            _series = _series.to_frame().reset_index()

        _series.rename(columns={self.student_id_column: "18 Digit ID"}, inplace=True)

        if self.report_name == "emergency_fund":
            if day_limit:
                _series.rename(
                    columns={"Amount": "amount_" + str(day_limit) + "_days"},
                    inplace=True,
                )
            else:
                _series.rename(columns={"Amount": "amount"}, inplace=True)

        _series.set_index("18 Digit ID", inplace=True)

        if day_limit == 7:
            self.seven_day_summary = _series
        elif day_limit == 30:
            self.thirty_day_summary = _series
        else:
            self.all_time_summary = _series
