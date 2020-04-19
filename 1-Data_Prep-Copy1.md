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
            print(self.report_name)
            _series.name = self.summary_column_name + \
                "_" + str(day_limit) + "_day"
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
            _series.rename(columns={'Amount': 'amount_' + str(day_limit)}, inplace=True)
        
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


```

```python
hs_reduced_columns = df_combined[[
    'Submitted Date', 'Student: High School Contact Id']]

hs_reduced_columns.rename(
    columns={'Student: High School Contact Id': '18 Digit ID'}, inplace=True)
```

```python
ps_reduced_columns = df_college[['Submitted Date', 'Student 18 Digit Id']]
ps_reduced_columns.rename(columns={'Student 18 Digit Id': '18 Digit ID'}, inplace=True)
```

```python
survey_df = pd.concat([ps_reduced_columns, hs_reduced_columns], axis=0, ignore_index=True, sort=True)

```

```python
survey_df['Submitted Date'] = pd.to_datetime(survey_df['Submitted Date'])

survey_df.rename(columns={'Submitted Date': 'Date'}, inplace=True)
```

```python
master_df = files['roster'].df.copy()
```

```python
def prep_master_df_with_counts(files, master_df):

    for file in files:
        if file == 'roster':
            continue
        master_df = master_df.merge(
            files[file].seven_day_summary, how='left', on='18 Digit ID'
        )
        master_df = master_df.merge(
            files[file].thirty_day_summary, how='left', on='18 Digit ID'
        )
        master_df = master_df.merge(
            files[file].all_time_summary, how='left', on='18 Digit ID'
        )
    return master_df
```

```python
master_df = prep_master_df_with_counts(files, master_df)
```

```python
survey_dfs = [survey_df]
survey_dfs = [{"time_period": "",
               "df": survey_df}]


for i in [7, 30]:
    _dict = {}

    _dict['time_period'] = "_" + str(i) + "_days"
    _dict['df'] = (survey_df[survey_df['Date'] >= (
        datetime.now() - timedelta(days=i))])

    survey_dfs.append(_dict)
```

```python
for i in survey_dfs:
    master_df['took_survey' + i['time_period']] = master_df['18 Digit ID'].isin(i['df']['18 Digit ID'])
```

```python
# 7 Days
# Total Contacts 7 Days
df_file4['total_contacts_7_days'] = (df_file4.activity_count_7_day.add(
    df_file4.outgoing_sms_count_7_day, fill_value=0).add(df_file4.workshops_attendend_7_days, fill_value=0).add(df_file4.case_note_count_7_day, fill_value=0))

df_file4['been_contacted_7_days'] = df_file4['total_contacts_7_days'] > 0

# Total Contacts Minus Text 7 Days
df_file4['been_contacted_minis_text_7_days'] = (df_file4.activity_count_7_day).add(
    df_file4.workshops_attendend_7_days, fill_value=0).add(df_file4.case_note_count_7_day, fill_value=0) > 0 


# Total Reciprocal 7 Days
df_file4['total_reciprocal_communication_7_days'] = (df_file4.incoming_sms_count_7_day.add(
    df_file4.reciprocal_count_7_day, fill_value=0).add(df_file4.took_survey_7_days, fill_value=0).add(df_file4.workshops_attendend_7_days, fill_value=0).add(df_file4.case_note_count_7_day, fill_value=0))
df_file4['reciprocal_communication_7_days'] = df_file4['total_reciprocal_communication_7_days'] > 0

# Workshops 7 Days
df_file4['attended_at_least_one_workshop_7_days'] = (
    df_file4.workshops_attendend_7_days > 0)
```

```python
# Total Contacts 30 Days
df_file4['total_contacts_30_days'] = (df_file4.activity_count_30_day.add(
    df_file4.outgoing_sms_count_30_day, fill_value=0).add(df_file4.workshops_attendend_30_days, fill_value=0).add(df_file4.case_note_count_30_day, fill_value=0))
df_file4['been_contacted_30_days'] = df_file4['total_contacts_30_days'] > 0


# Total Contacts Minus Text 30 Days
df_file4['been_contacted_minis_text_30_days'] = (
    df_file4.activity_count_30_day).add(
    df_file4.workshops_attendend_30_days, fill_value=0).add(df_file4.case_note_count_30_day, fill_value=0) > 0 


# Total Reciprocal 30 Days

df_file4['total_reciprocal_communication_30_days'] = (df_file4.incoming_sms_count_30_day.add(
    df_file4.reciprocal_count_30_day, fill_value=0).add(df_file4.took_survey_30_days, fill_value=0).add(df_file4.workshops_attendend_30_days, fill_value=0).add(df_file4.case_note_count_30_day, fill_value=0))

df_file4['reciprocal_communication_30_days'] = df_file4['total_reciprocal_communication_30_days'] > 0


# Workshops 30 days
df_file4['attended_at_least_one_workshop_30_days'] = (
    df_file4.workshops_attendend_30_days > 0)
```

```python
# Total Contacts
df_file4['total_contacts'] = (df_file4.activity_count.add(
    df_file4.outgoing_sms_count, fill_value=0).add(df_file4.workshops_attendend, fill_value=0).add(df_file4.case_note_count, fill_value=0))

df_file4['been_contacted'] = df_file4['total_contacts'] > 0

# Total Contacts Minus Text
df_file4['been_contacted_minis_text'] = (df_file4.activity_count).add(
    df_file4.workshops_attendend, fill_value=0).add(df_file4.case_note_count, fill_value=0) > 0


# Total Reciprocal Communication
df_file4['total_reciprocal_communication'] = (df_file4.incoming_sms_count.add(
    df_file4.reciprocal_count, fill_value=0).add(df_file4.took_survey, fill_value=0).add(df_file4.workshops_attendend, fill_value=0).add(df_file4.case_note_count, fill_value=0))

df_file4['reciprocal_communication'] = df_file4['total_reciprocal_communication'] > 0

# Worksops
df_file4['attended_at_least_one_workshop'] = (df_file4.workshops_attendend > 0)
```

```python
# File 1
# df = helpers.shorten_site_names(df)
# df = helpers.clean_column_names(df)

# File 2
# df_file2 = helpers.shorten_site_names(df_file2)
# df_file2 = helpers.clean_column_names(df_file2)
```

### Save output file into processed directory

Save a file in the processed directory that is cleaned properly. It will be read in and used later for further analysis.

```python
df_file4['student_count'] = 1
```

```python
# df_file4.loc[df['Contact Record Type'] == "Student: High School", 'Contact Record Type'] = "High School"
# df_file4.loc[df['Contact Record Type'] == "Student: Post-Secondary", 'Contact Record Type'] = "Post-Secondary"
```

```python
# df_file4 = helpers.shorten_site_names(df_file4)
df_file5 = helpers.shorten_site_names(df_file5)

```

```python
# Save File 1 Data Frame (Or master df)
df_file4.to_pickle(summary_file)
```

```python
# df_file4 = df_file4.applymap(lambda x: 1 if x == True else x)
# df_file4 = df_file4.applymap(lambda x: 0 if x == False else x)
```

```python
# df_file4.to_csv('student_comms.csv',index=False)
```

```python
google_sheet = Spread('1tEzcIDba-dF0M4uMHUt2fwOAtO91U8q6TUFPBp9TSbY')


# google_sheet.df_to_sheet(df_file4, index=False, sheet='Sheet1', start='A1', replace=True)
 
```

```python
google_sheet.df_to_sheet(df_file5, index=True, sheet='Emergency Fund', start='A1', replace=True)

```

```python
update_date = datetime.now().date().strftime("%m/%d/%y")

```

```python
google_sheet.update_cells(start='A1',end="A2", sheet="Updated", vals=[
                          'Updated:', update_date])
```

```python

```
