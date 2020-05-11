import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import helpers
import os
import numpy as np
from reportforce import Reportforce
from gspread_pandas import Spread, Client, conf
import load_data
from classes import SalesforceReport
from variables import (
    files_prep,
    activities,
    reciprocal_activities,
    ACTIVITIES_GOOGLE_SHEET,
    threshold_frames,
    regions,
    GOOGLE_SHEET_UPLOAD,
)

import prep_data
from dotenv import load_dotenv

load_dotenv()


GSPREAD_PANDAS_CONFIG_DIR = os.environ.get("GSPREAD_PANDAS_CONFIG_DIR")
SF_PASS = os.environ.get("SF_PASS")
SF_TOKEN = os.environ.get("SF_TOKEN")
SF_USERNAME = os.environ.get("SF_USERNAME")

config = conf.get_config(GSPREAD_PANDAS_CONFIG_DIR)


sf = Reportforce(username=SF_USERNAME, password=SF_PASS, security_token=SF_TOKEN)
# conf.get_config


def main():

    # FOR TESTING
    # files = load_data.setup_classes(files_prep)
    # files = load_data.setup_activities_files(files, activities, reciprocal_activities)
    # load_data.read_from_csv(files)

    # FOR PRODUCTION
    files = load_data.setup_classes(files_prep)
    load_data.load_from_salesforce(files_prep, files, sf)
    files = load_data.setup_activities_files(files, activities, reciprocal_activities)
    files = load_data.load_activities_files(files, ACTIVITIES_GOOGLE_SHEET, config)
    load_data.by_pass_csv(files)

    load_data.convert_all_files_date_column(files)

    # Generating Over time files

    list_of_counts = prep_data.create_list_of_counts(files)
    total_reciprocal_counts = prep_data.create_total_counts(list_of_counts)
    total_reciprocal_counts = prep_data.adjust_count_dates(total_reciprocal_counts)
    roster_subset = files["roster"].df[
        ["18 Digit ID", "Site", "High School Class", "Contact Record Type"]
    ]
    roster_with_count = prep_data.create_roster_with_counts(
        roster_subset, total_reciprocal_counts
    )
    site_count = prep_data.create_site_count(roster_with_count)
    site_count_with_enrollments = prep_data.create_site_count_with_enrollments(
        roster_subset, site_count
    )
    site_count_with_enrollments = helpers.shorten_site_names(
        site_count_with_enrollments
    )
    site_count_with_enrollments["Region"] = site_count_with_enrollments.apply(
        lambda x: prep_data.append_region(x["Site"], regions), axis=1
    )
    # Generating Summary Files

    prep_data.generate_summary_frames(files)
    master_df = files["roster"].df.copy()

    master_df.set_index("18 Digit ID", inplace=True)

    master_df = prep_data.prep_master_df_with_counts(files, master_df)
    master_df = prep_data.count_of_key_areas(master_df, threshold_frames)
    master_df = prep_data.determine_if_met_threshold(master_df, threshold_frames)

    summary_table = prep_data.create_summary_tables(master_df)
    summary_table.rename(columns={"index": "Site"}, inplace=True)
    summary_table = helpers.shorten_site_names(summary_table)
    summary_table.loc[
        summary_table["time_period"] == "7 Days", "time_period"
    ] = "Last Week"

    # Preping Emergency Fund
    files["emergency_fund"].df = helpers.shorten_site_names(files["emergency_fund"].df)
    files["emergency_fund"].df["Week"] = files["emergency_fund"].df[
        "Date"
    ] - pd.TimedeltaIndex(files["emergency_fund"].df.Date.dt.dayofweek, unit="d")
    emergency_fund = files["emergency_fund"].df.pivot_table(
        index="Week", columns="Site", values="Amount", aggfunc="sum"
    )

    # Upload Data

    google_sheet = Spread(GOOGLE_SHEET_UPLOAD, config=config)

    google_sheet.df_to_sheet(
        summary_table, index=False, sheet="Aggregate Data", start="A1", replace=True,
    )

    google_sheet.df_to_sheet(
        site_count_with_enrollments,
        index=False,
        sheet="Reciprocal Overtime",
        start="A1",
        replace=True,
    )

    google_sheet.df_to_sheet(
        emergency_fund, index=True, sheet="Emergency Fund", start="A1", replace=True,
    )

    update_date = datetime.now().date().strftime("%m/%d/%y")

    google_sheet.update_cells(
        start="A1", end="A2", sheet="Updated", vals=["Updated:", update_date]
    )


if __name__ == "__main__":
    main()
