---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.2'
      jupytext_version: 1.3.0
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

## Student Communication

Reports on student communication during COVID

### Data Sources
- File 1 Logged Activities : https://ctgraduates.lightning.force.com/lightning/r/Report/00O1M0000077bWjUAI/view
- File 2 Incoming SMS:  https://ctgraduates.lightning.force.com/lightning/r/Report/00O1M0000077bWiUAI/view
- File 3 Outgoing SMS:  https://ctgraduates.lightning.force.com/lightning/r/Report/00O1M0000077bWTUAY/view?queryScope=userFolders
- File 4 Student Roster: https://ctgraduates.lightning.force.com/lightning/r/Report/00O1M0000077bWnUAI/view
- File 5 Emergency Funds: https://ctgraduates.lightning.force.com/lightning/r/Report/00O1M0000077cchUAA/view
- File 6 Workshops Attended: https://ctgraduates.lightning.force.com/lightning/r/Report/00O1M0000077bbYUAQ/view
- File 7 Case Nates: https://ctgraduates.lightning.force.com/lightning/r/Report/00O1M0000077c3cUAA/view

### Changes
- 04-05-2020 : Started project

```python
# ALWAYS RUN
# General Setup 

%load_ext dotenv
%dotenv

from salesforce_reporting import Connection, ReportParser
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import helpers
import os
import numpy as np
from reportforce import Reportforce
from gspread_pandas import Spread, Client



SF_PASS = os.environ.get("SF_PASS")
SF_TOKEN = os.environ.get("SF_TOKEN")
SF_USERNAME = os.environ.get("SF_USERNAME")

sf = Reportforce(username=SF_USERNAME, password=SF_PASS, security_token=SF_TOKEN)
```

### File Locations

```python
class SalesforceReport:
    def __init__(self, file_number, report_id, report_filter_column, report_name, date_column, summary_column_name, student_id_column):
        self.report_name = report_name
        self.file_numer = file_number
        self.report_id = report_id
        self.report_filter_column = report_filter_column
        self.salesforce_df = None
        self.df = None
        self.date_column = date_column
        self.summary_column_name = summary_column_name
        self.student_id_column = student_id_column

        self.in_file = "sf_output_file_new" + str(file_number) + ".csv"
        self.summary_file = "process_data_file_new" + str(file_number) + ".pkl"

        self.in_file_location = (Path.cwd() / "data" / "raw" / self.in_file)
        self.summary_file_location = (
            Path.cwd() / "data" / "raw" / self.summary_file)

        self.seven_day_summary = None
        self.thirty_day_summary = None
        self.all_time_summary = None

    def read_from_salesforce(self, sf):
        self.salesforce_df = sf.get_report(
            self.report_id, id_column=self.report_filter_column)

    def write_csv(self, index=False):
        self.salesforce_df.to_csv(self.in_file_location, index=index)

    def read_csv(self):
        self.df = pd.read_csv(self.in_file_location)

    def write_pkl(self):
        self.df.to_pickle(sellf.summary_file_location)

    def convert_date_column(self):
        self.df[self.date_column] = pd.to_datetime(self.df[self.date_column])
        if self.date_column != "Date":
            self.df.rename(columns={self.date_column: "Date"}, inplace=True)

    def create_summary(self, day_limit=None, sum_type="count"):
        if day_limit:
            _df = self.df[self.df.Date >= (
                datetime.now() - timedelta(days=day_limit))]
        else:
            _df = self.df.copy()

        if sum_type == "count":
            _series = _df.groupby(self.student_id_column).size()
        elif sum_type == "sum":
            _series = _df.groupby(self.student_id_column).sum()

        if day_limit:
            _series.name = self.summary_column_name + \
                "_" + str(day_limit) + "_days"
        else:
            _series.name = self.summary_column_name
        _series.index.names = ['18 Digit ID']

        if isinstance(_series, pd.DataFrame):
            _series = _series.reset_index()

        else:
            _series = _series.to_frame().reset_index()

        _series.rename(
            columns={self.student_id_column: "18 Digit ID"}, inplace=True)

        if self.report_name == "emergency_fund":
            if day_limit:
                _series.rename(columns={'Amount': 'amount_' + str(day_limit) + "_days"}, inplace=True)
            else:
                _series.rename(columns={'Amount': 'amount'}, inplace=True)
        
        _series.set_index('18 Digit ID', inplace=True)
        
        if day_limit == 7:
            self.seven_day_summary = _series
        elif day_limit == 30:
            self.thirty_day_summary = _series
        else:
            self.all_time_summary = _series
```

```python
files_prep = [
    {
        "name": "incoming_sms",
        "id": "00O1M0000077bWiUAI",
        "report_filter_column": "Incoming SMS: ID",
        'date_column': 'Incoming SMS: Created Date',
        'summary_column_name': 'incoming_sms_count',
        'student_id_column': 'Contact: 18 Digit ID',
    },
    {
        "name": "emergency_fund",
        "id": "00O1M0000077cchUAA",
        "report_filter_column": "18 Digit ID",
        "date_column": "Date",
        "summary_column_name": "Amount",
        "student_id_column": "18 Digit ID"

    },
    {
        "name": "roster",
        "id": "00O1M0000077bWnUAI",
        "report_filter_column": "18 Digit ID",
        "date_column": None,
        "summary_column_name": "NA",
        "student_id_column": "NA"

    },
    {
        "name": "outgoing_sms",
        "id": "00O1M0000077bWTUAY",
        "report_filter_column": "SMS History: Record number",
        "date_column": "SMS History: Created Date",
        "summary_column_name": "outgoing_sms_count",
        "student_id_column": "Contact: 18 Digit ID"

    }, 
    {
        "name": "workshops",
        "id": "00O1M0000077bbYUAQ",
        "report_filter_column": "Workshop Session Attendance: Workshop Session Attendance Name",
        "date_column": "Date",
        "summary_column_name": "workshop_count",
        "student_id_column": "18 Digit ID"

    },   
    {
        "name": "case_notes",
        "id": "00O1M0000077c3cUAA",
        "report_filter_column": "Case Note: Case Note ID",
        "date_column": "Date",
        "summary_column_name": "case_note_count",
        "student_id_column": "Academic Term: 18 Digit Student ID"

    },       
    
]
```

```python
def setup_classes(file_prep):
    _files = {}
    for i in range(len(files_prep)):
        file_number = i + 1

        file_title = files_prep[i]['name']

        _files[file_title] = SalesforceReport(
            file_number, files_prep[i]["id"],
            files_prep[i]["report_filter_column"], files_prep[i]['name'],
            files_prep[i]['date_column'],files_prep[i]['summary_column_name'],
            files_prep[i]['student_id_column']
            
        )
    return _files
```

```python
def load_from_salesforce(files_prep, files):
       for i in range(len(files_prep)):
            file_title = files_prep[i]['name']
            files[file_title].read_from_salesforce(sf)
            files[file_title].write_csv()
            

    
```

```python
def read_from_csv(files):
    for file_title in files:
        files[file_title].read_csv()
        
        if files[file_title].date_column:
            files[file_title].convert_date_column()
    
```

```python


def generate_summary_frames(files):
    days_to_check = [7, 30, None]

    
    for file in files:
        if file == 'roster':
            continue

        for day_limit in days_to_check:
            if file == "emergency_fund":
                files[file].create_summary(day_limit, sum_type='sum')
            else:
                files[file].create_summary(day_limit)
        
```

```python
# file_number, report_id, report_filter_column, report_name, date_column, summary_column_name, student_id_column


files = setup_classes(files_prep)

# load_from_salesforce(files_prep, files)

files['activities'] = SalesforceReport(
    len(files) + 1, '00O1M0000077bWjUAI',
    'Activity ID', 'activities', 'Date',
    'activity_count', '18 Digit ID')

files['reciprocal_activities'] = SalesforceReport(
    len(files) + 1, '00O1M0000077bWjUAI',
    'Activity ID', 'reciprocal_activity', 'Date',
    'reciprocal_activity_count', '18 Digit ID')


# activity_google_sheet = Spread('1r3YGO2PMz7tVu3duCN1stQG_phFFKOjW0KZO9XKgoP8')
# activity_google_sheet.open_sheet(0)

# activities_df = activity_google_sheet.sheet_to_df().reset_index()
# activities_df = activities_df.astype({'Reciprocal Communication': 'int32'})

# reciprocol_df = activities_df[activities_df['Reciprocal Communication'] > 0]

# files['activities'].salesforce_df = activities_df
# files['reciprocal_activities'].salesforce_df = reciprocol_df


# files['activities'].write_csv()
# files['reciprocal_activities'].write_csv()





read_from_csv(files)
```

```python
# Open Google Sheet Files
spanish_survey = Spread('1ViRSTuhmrEt4dAQVOvHXoDL_oqjwOjE3Ox4PLGBA7b0')
spanish_survey.open_sheet(0)
df_spanish = spanish_survey.sheet_to_df(index=None)


english_survey = Spread('1B8XobOuEa9gKOdxHzbbaZ4P2qjEEcmN9p3m6UikXSlk')
english_survey.open_sheet(0)
df_english = english_survey.sheet_to_df(index=None)

english_survey.open_sheet(1)
df_english_second_sheet = english_survey.sheet_to_df(index=None)

college_survey = Spread('1c253r4eAVCMi0kHil_xMfX6OYP9YHHe5NY52b-WeFt8')
college_survey.open_sheet(0)
df_college_old = college_survey.sheet_to_df(index=None)

college_survey.open_sheet(1)
df_college_new = college_survey.sheet_to_df(index=None)



# Combined Spanish and English HS Surveys
df_spanish.columns = df_english.columns
df_combined = pd.concat([df_english, df_spanish, df_english_second_sheet], axis=0, ignore_index=True)

# Combine Old College Responses (old meaning before connected to Google Sheets and the new responses)
df_college = pd.concat([df_college_old, df_college_new], axis=0, ignore_index=True)


hs_reduced_columns = df_combined[[
    'Submitted Date', 'Student: High School Contact Id']]

hs_reduced_columns.rename(
    columns={'Student: High School Contact Id': '18 Digit ID'}, inplace=True)



ps_reduced_columns = df_college[['Submitted Date', 'Student 18 Digit Id']]
ps_reduced_columns.rename(columns={'Student 18 Digit Id': '18 Digit ID'}, inplace=True)





```

```python
survey_location = (Path.cwd() / "data" / "raw" / "survey.csv")

survey_df_prep = pd.concat([ps_reduced_columns, hs_reduced_columns], axis=0, ignore_index=True, sort=True)


survey_df_prep.to_csv(survey_location, index=False)
```

```python
survey_df = pd.read_csv(survey_location)
```

```python
files['survey'] = SalesforceReport(len(
    files) + 1, "NA", "NA", "survey", "Submitted Date", "took_survey", "18 Digit ID")
```

```python
files['survey'].salesforce_df = pd.concat([ps_reduced_columns, hs_reduced_columns], axis=0, ignore_index=True, sort=True)
```

```python
files['survey'].write_csv()
```

```python
files['survey'].read_csv()
```

```python
files['survey'].convert_date_column()
```

```python
generate_summary_frames(files)
```

```python
master_df = files['roster'].df.copy()
```

```python
master_df.set_index('18 Digit ID', inplace=True)
```

```python
def prep_master_df_with_counts(files, master_df):

    for file in files:
        if file == 'roster':
            continue
        master_df = master_df.merge(
            files[file].seven_day_summary, how='left', left_index=True, right_index=True
        )
        master_df = master_df.merge(
            files[file].thirty_day_summary, how='left', left_index=True, right_index=True
        )
        master_df = master_df.merge(
            files[file].all_time_summary, how='left', left_index=True, right_index=True
        )
    return master_df
```

```python
master_df = prep_master_df_with_counts(files, master_df)
```

```python
threshold_frames = {
    'outreach': ['activity_count', 'outgoing_sms_count', 'workshop_count', 'case_note_count'],
    "outreach_minus_text": ['activity_count', 'workshop_count', 'case_note_count'],
    "reciprocal": ['incoming_sms_count', 'reciprocal_activity_count', 'took_survey', 'case_note_count', 'workshop_count'],
    "workshop": ['workshop_count'] 
}


def count_of_key_areas(master_df, threshold_frames):
    time_periods = ["", "_7_days", "_30_days"]

    for key, items in threshold_frames.items():

        for time_period_name in time_periods:
            master_df['total_' + key + time_period_name] = 0
            for item in items:
                master_df_column = 'total_' + key + time_period_name
                sub_column = item + time_period_name
#                 print("column adding:", sub_column)
#                 print("sum of master column:", master_df[master_df_column].sum())
#                 print("sum of sub column:", master_df[sub_column].sum())
#                 print("sum of two columns: ", (master_df[master_df_column].add(master_df[sub_column], fill_value=0)).sum())
                

                master_df[master_df_column] = master_df[master_df_column].add(master_df[sub_column], fill_value=0)
                
#                 print('master_df value after add:', master_df[master_df_column].sum())
#                 print('break')

    return master_df
```

```python
def determine_if_met_threshold(master_df, threshold_frames):
    time_periods = ["", "_7_days", "_30_days"]

    for key in threshold_frames.keys():
        for time_period_name in time_periods:
            column_name = "met_" + key + time_period_name
            check_column = 'total_' + key + time_period_name

            master_df[column_name] = master_df[check_column] > 0
        
    return master_df
```

```python
master_df = count_of_key_areas(master_df,threshold_frames)
```

```python
master_df = determine_if_met_threshold(master_df, threshold_frames)
```

```python
 def create_table_for_report(df, percent_column, count_column, time_period, measure, include_ps=True, workshop=False):
    if time_period == "":
        time_period_text = "Since March 1st"
    else:
        time_period_text = str(time_period) + " Days"

    hs_df = df[df['Contact Record Type'] == "Student: High School"]
    count_table_hs = pd.pivot_table(
        data=hs_df, index='Site', values=count_column, aggfunc='sum', margins=False)
    percent_table_hs = pd.crosstab(
        hs_df['Site'], hs_df[percent_column], normalize=False, margins=False)

    student_count_hs = pd.DataFrame(hs_df['Site'].value_counts()).rename(
        columns={"Site": "Student Count"})

    if workshop == True:
        count_table_hs.rename(
            columns={count_column: "Count of Workshop Sessions"}, inplace=False)

    count_table_hs.rename(
        columns={count_column: "Count of " + measure}, inplace=True)

    percent_table_hs = percent_table_hs.drop(columns=False)
    percent_table_hs.rename(
        columns={True: "Numerator of Site's Students " + measure}, inplace=True)
    table_hs = pd.concat([count_table_hs, percent_table_hs], axis=1, sort=True)
    table_hs["Numerator of Site's Students " + measure] = (
        table_hs["Numerator of Site's Students " + measure])
    table_hs['record_type'] = "High School"
    table_hs['time_period'] = time_period_text

    table_hs = pd.concat([table_hs, student_count_hs], axis=1, sort=True).reset_index()

    if include_ps == True:
        college_df = df[df['Contact Record Type'] == "Student: Post-Secondary"]
        count_table_ps = pd.pivot_table(
            data=college_df, index='Site', values=count_column, aggfunc='sum', margins=False)
        percent_table_ps = pd.crosstab(
            college_df['Site'], college_df[percent_column], normalize=False, margins=False)
        count_table_ps.rename(
            columns={count_column: "Count of " + measure}, inplace=True)
        percent_table_ps = percent_table_ps.drop(columns=False)
        percent_table_ps.rename(
            columns={True: "Numerator of Site's Students " + measure}, inplace=True)
        table_college = pd.concat([count_table_ps, percent_table_ps], axis=1, sort=True)
#         table_college["Numerator of Site's Students " + measure] = (
#             table_college["Numerator of Site's Students " + measure])
        table_college['record_type'] = "Post-Secondary"
        table_college['time_period'] = time_period_text

        student_count_college = pd.DataFrame(college_df['Site'].value_counts()).rename(
            columns={"Site": "Student Count"})
        table_college = pd.concat(
            [table_college, student_count_college], axis=1, sort=True).reset_index()

        return table_hs.append(table_college)
    else:

        return table_hs
```

```python
been_contacted_table = create_table_for_report(
    master_df, "met_outreach_30_days", 'total_outreach_30_days', 30, 'all_contacts')
```

```python
def create_summary_tables(df):
    time_periods = ['', 7, 30]
    merge_columns = ['index', 'record_type', 'time_period', 'Student Count']
    _complete_table = pd.DataFrame()
    for time_period in time_periods:
        if time_period != "":
            column_text = "_" + str(time_period) + "_days"
        else:
            column_text = ""
        _outreach_table = create_table_for_report(
            master_df, "met_outreach" + column_text, 'total_outreach' +
            column_text, time_period, 'all_contacts')

        _outreach_minus_text = create_table_for_report(
            master_df, "met_outreach_minus_text" + column_text, 'total_outreach_minus_text'+column_text, time_period, 'all_contacts_no_text')

        _reciprocal_communication_table = create_table_for_report(
            df, 'met_reciprocal' + column_text, "total_reciprocal" + column_text, time_period, 'reciprocal_communication')

        _workshop_table = create_table_for_report(
            df, 'met_workshop' + column_text, "workshop_count" + column_text, time_period, 'workshops', include_ps=False, workshop=True)
        
   
        _table = _outreach_table.merge(_outreach_minus_text, on=merge_columns)

        _table = _table.merge(_reciprocal_communication_table, on=merge_columns)

        _table = _table.merge(_workshop_table, on=merge_columns, how='outer')
        
        _complete_table = _complete_table.append(_table)
        
        
        
            
    return _complete_table
        
        
```

```python
summary_table = create_summary_tables(master_df)
```

```python
summary_table.rename(columns={'index': 'Site'},inplace=True)
```

```python
summary_table = helpers.shorten_site_names(summary_table)

```

```python
google_sheet = Spread('1tEzcIDba-dF0M4uMHUt2fwOAtO91U8q6TUFPBp9TSbY')


google_sheet.df_to_sheet(summary_table, index=False, sheet='Aggregate Data', start='A1', replace=True)


google_sheet.df_to_sheet(files['emergency_fund'].df, index=True, sheet='Emergency Fund', start='A1', replace=True)

update_date = datetime.now().date().strftime("%m/%d/%y")

google_sheet.update_cells(start='A1',end="A2", sheet="Updated", vals=[
                          'Updated:', update_date])
```
