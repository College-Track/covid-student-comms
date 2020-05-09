import pandas as pd
from classes import SalesforceReport
from gspread_pandas import Spread, Client
import load_data


def setup_classes(files_prep):
    _files = {}
    for i in range(len(files_prep)):
        file_number = i + 1

        file_title = files_prep[i]["name"]

        _files[file_title] = SalesforceReport(
            file_number,
            files_prep[i]["id"],
            files_prep[i]["report_filter_column"],
            files_prep[i]["name"],
            files_prep[i]["date_column"],
            files_prep[i]["summary_column_name"],
            files_prep[i]["student_id_column"],
        )
    return _files


def load_from_salesforce(files_prep, files, sf):
    for i in range(len(files_prep)):
        file_title = files_prep[i]["name"]
        files[file_title].read_from_salesforce(sf)


def write_all_csvs(files):
    for file_title in files:
        files[file_title].write_csv()


def by_pass_csv(files):
    for file_title in files:
        files[file_title].bypass_csv()


def convert_all_files_date_column(files):
    for file_title in files:
        if files[file_title].date_column:
            files[file_title].convert_date_column()


def read_from_csv(files):
    for file_title in files:
        files[file_title].read_csv()


def write_to_pkl(files):
    for file_title in files:
        files[file_title].write_pkl()


def load_from_google_sheets(sheet_id, sheet_number):
    _sheet = Spread(sheet_id)
    _sheet.open_sheet(sheet_number)

    _df = _sheet.sheet_to_df().reset_index()
    return _df


def setup_activities_files(files, activities, reciprocal_activities):
    files["activities"] = SalesforceReport(len(files) + 1, *activities)

    files["reciprocal_activities"] = SalesforceReport(
        len(files) + 1, *reciprocal_activities
    )

    return files


def load_activities_files(files, sheet_id):
    activities_df = load_data.load_from_google_sheets(sheet_id, 0)
    activities_df = activities_df.astype({"Reciprocal Communication": "int32"})
    reciprocol_df = activities_df[activities_df["Reciprocal Communication"] > 0]
    files["activities"].salesforce_df = activities_df
    files["reciprocal_activities"].salesforce_df = reciprocol_df

    return files
