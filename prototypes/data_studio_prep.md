---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.2'
      jupytext_version: 1.4.2
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
- File 8 Survey: https://ctgraduates.lightning.force.com/lightning/r/Report/00O1M000007R6FrUAK/edit

### Changes
- 04-05-2020 : Started project

```python

```

```python
%load_ext autoreload
%autoreload 2
# ALWAYS RUN
# General Setup 
%load_ext dotenv
%dotenv
```

```python
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import helpers
import os
import numpy as np
from reportforce import Reportforce
from gspread_pandas import Spread, Client
from classes import (SalesforceReport,
                     setup_classes,
                     load_from_salesforce,
                     read_from_csv,
                     write_to_pkl,
                     generate_summary_frames)


SF_PASS = os.environ.get("SF_PASS")
SF_TOKEN = os.environ.get("SF_TOKEN")
SF_USERNAME = os.environ.get("SF_USERNAME")

sf = Reportforce(username=SF_USERNAME, password=SF_PASS,
                 security_token=SF_TOKEN)
```

### File Loading

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
    {
        "name": "survey",
        "id": "00O1M000007R6FrUAK",
        "report_filter_column": '18 Digit ID',
        'date_column': "Completed CT 2019-20 Survey: Date",
        "summary_column_name": "took_survey",
        "student_id_column": "18 Digit ID"
    }
#     {
#         "name": "activities",
#         "id": "00O1M0000077bWjUAI",
#         "report_filter_column": '18 Digit Activity ID',
#         'date_column': "Date",
#         "summary_column_name": "activity_count",
#         "student_id_column": "18 Digit ID"
#     }

]
```

```python
files = setup_classes(files_prep)

load_from_salesforce(files_prep, files, sf)
```

```python
# file_number, report_id, report_filter_column, report_name, date_column, summary_column_name, student_id_column


files['activities'] = SalesforceReport(
    len(files) + 1, '00O1M0000077bWjUAI',
    'Activity ID', 'activities', 'Date',
    'activity_count', '18 Digit ID')

files['reciprocal_activities'] = SalesforceReport(
    len(files) + 1, '00O1M0000077bWjUAI',
    'Activity ID', 'reciprocal_activity', 'Date',
    'reciprocal_activity_count', '18 Digit ID')


activity_google_sheet = Spread('1r3YGO2PMz7tVu3duCN1stQG_phFFKOjW0KZO9XKgoP8')
activity_google_sheet.open_sheet(0)

activities_df = activity_google_sheet.sheet_to_df().reset_index()
activities_df = activities_df.astype({'Reciprocal Communication': 'int32'})

reciprocol_df = activities_df[activities_df['Reciprocal Communication'] > 0]

files['activities'].salesforce_df = activities_df
files['reciprocal_activities'].salesforce_df = reciprocol_df


files['activities'].write_csv()
files['reciprocal_activities'].write_csv()

```

```python
read_from_csv(files)
```

```python
def adjust_date(old_date, new_date):
    if pd.isna(old_date):
        return (new_date)
    else:
        return old_date
```

```python
files['activities'].df['Date'] = files['activities'].df.apply(lambda x: adjust_date(x['Date'], x['Date of Contact']),axis=1)
```

```python
files['reciprocal_activities'].df['Date'] = files['reciprocal_activities'].df.apply(
    lambda x: adjust_date(x['Date'], x['Date of Contact']), axis=1)
```

```python
files['activities'].df['Date'] = pd.to_datetime(files['activities'].df['Date'])
```

```python
files['reciprocal_activities'].df['Date'] = pd.to_datetime(files['reciprocal_activities'].df['Date'])
```

### Creating Overtime Data Frame

```python
# Reciprocal Includes: Reciprocal, Incoming SMS, Survey, Case Notes, Workshops, and Survey
```

```python
def group_by_date(file, student_id, files=files):
    _df = files = files[file].df.groupby([student_id, 'Date']).size()
    
    _df.rename_axis(['18 Digit ID', "Date"],inplace=True)
    
    return _df
```

```python
recip_activity_count = group_by_date('reciprocal_activities', '18 Digit ID')
incoming_sms_count = group_by_date('incoming_sms', 'Contact: 18 Digit ID')
survey_count = group_by_date('survey', '18 Digit ID')
case_note_count = group_by_date(
    'case_notes', 'Academic Term: 18 Digit Student ID')
workshops_count = group_by_date('workshops', '18 Digit ID')

list_of_counts = [recip_activity_count, incoming_sms_count,case_note_count,
                  survey_count, workshops_count]
```

```python
totoal_reciprocal_count = recip_activity_count.add(incoming_sms_count, fill_value=0)
for grouping in list_of_counts[2:]:
    totoal_reciprocal_count = totoal_reciprocal_count.add(grouping, fill_value=0)
```

```python
totoal_reciprocal_count = pd.DataFrame(totoal_reciprocal_count)
totoal_reciprocal_count.reset_index(inplace=True)
totoal_reciprocal_count.rename(columns={0:"Count"},inplace=True)
```

```python
totoal_reciprocal_count['Date'] = pd.to_datetime(totoal_reciprocal_count['Date'])
```

```python
totoal_reciprocal_count['Date'] = totoal_reciprocal_count['Date'] - \
    pd.TimedeltaIndex(totoal_reciprocal_count.Date.dt.strftime("%w").astype(int), unit='d')
```

```python
roster_subset = files['roster'].df[['18 Digit ID', 'Site', "High School Class", "Contact Record Type"]]
```

```python
roster_with_count = roster_subset.merge(totoal_reciprocal_count, on='18 Digit ID', how='left')
roster_with_count['Date'] = roster_with_count['Date'].dt.date
```

```python
roster_with_count['Date'] = pd.to_datetime(roster_with_count['Date'])
```

```python
roster_with_count = roster_with_count[roster_with_count['Count'] > 0]
```

```python
site_count = roster_with_count.groupby(
    ['Site', 'High School Class', 'Contact Record Type', 'Date'])['18 Digit ID'].nunique()
```

```python
site_count = pd.DataFrame(site_count).reset_index()
site_count.rename(columns={'18 Digit ID':"Number of Students"}, inplace=True)
```

```python
site_count['Date'] = pd.to_datetime(site_count['Date'])
```

```python
a
```

```python
site_count_with_enrollments = site_count.merge(roster_enrollment_count, on=[
                                               'Site', 'High School Class', 'Contact Record Type'], how='left')
```

```python
site_count_with_enrollments['Date'] = pd.to_datetime(site_count_with_enrollments['Date'])
```

```python
site_count_with_enrollments = site_count_with_enrollments[site_count_with_enrollments['Date'] >= datetime(2020, 3,1)]
site_count_with_enrollments = site_count_with_enrollments[site_count_with_enrollments['Date'] < datetime.now()]
```

### Generating Summaries

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
master_df.to_pickle('data/processed/summary_file.pkl')
```

### Creating Site Based Summary

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
summary_table.loc[summary_table['time_period'] == "7 Days", 'time_period'] = 'Last Week'
```

### Writing Data

```python
files['emergency_fund'].df = helpers.shorten_site_names(files['emergency_fund'].df)
```

```python
files['emergency_fund'].df['Week'] = files['emergency_fund'].df['Date'] - \
    pd.TimedeltaIndex(files['emergency_fund'].df.Date.dt.dayofweek, unit='d')
```

```python
emergency_fund = files['emergency_fund'].df.pivot_table(index='Week', columns='Site', values='Amount', aggfunc='sum')
```

```python
emergency_fund = emergency_fund.reset_index()
```

```python
site_count_with_enrollments = helpers.shorten_site_names(site_count_with_enrollments)
```

```python
regions = {"NOLA": ["New Orleans"],
          "NOR CAL": ["Sacramento", "Oakland", "San Francisco", "East Palo Alto"],
          "LA": ['Watts', 'Boyle Heights'],
          "DC": ['Ward 8', 'The Durant Center'],
          'CO':["Denver", "Aurora"]}
```

```python
def append_region(site, regions):
    for region, sites in regions.items():
        if site in sites:
            return region
        else:
            continue
```

```python
site_count_with_enrollments['Region'] = site_count_with_enrollments.apply(
    lambda x: append_region(x['Site'], regions), axis=1)
```

```python
google_sheet = Spread('1tEzcIDba-dF0M4uMHUt2fwOAtO91U8q6TUFPBp9TSbY')

```

```python

google_sheet.df_to_sheet(summary_table, index=False, sheet='Aggregate Data', start='A1', replace=True)


google_sheet.df_to_sheet(site_count_with_enrollments, index=False, sheet='Reciprocal Overtime', start='A1', replace=True)


google_sheet.df_to_sheet(emergency_fund, index=False, sheet='Emergency Fund', start='A1', replace=True)



update_date = datetime.now().date().strftime("%m/%d/%y")

google_sheet.update_cells(start='A1',end="A2", sheet="Updated", vals=[
                          'Updated:', update_date])
```

```python
google_sheet.df_to_sheet(master_df, index=True, sheet='Raw', start='A1', replace=True)

```
