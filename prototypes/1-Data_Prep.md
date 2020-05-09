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
# ALWAYS RUN
today = datetime.today()


in_file1 = Path.cwd() / "data" / "raw" / "sf_output_file1.csv"
summary_file = Path.cwd() / "data" / "processed" / "processed_data.pkl"


in_file2 = Path.cwd() / "data" / "raw" / "sf_output_file2.csv"
summary_file2 = Path.cwd() / "data" / "processed" / "processed_data_file2.pkl"


in_file3 = Path.cwd() / "data" / "raw" / "sf_output_file3.csv"
summary_file3 = Path.cwd() / "data" / "processed" / "processed_data_file3.pkl"


in_file4 = Path.cwd() / "data" / "raw" / "sf_output_file4.csv"
summary_file4 = Path.cwd() / "data" / "processed" / "processed_data_file4.pkl"

in_file5 = Path.cwd() / "data" / "raw" / "sf_output_file5.csv"
summary_file5 = Path.cwd() / "data" / "processed" / "processed_data_file5.pkl"

in_file6 = Path.cwd() / "data" / "raw" / "sf_output_file6.csv"
summary_file6 = Path.cwd() / "data" / "processed" / "processed_data_file6.pkl"

in_file7 = Path.cwd() / "data" / "raw" / "sf_output_file7.csv"
summary_file7 = Path.cwd() / "data" / "processed" / "processed_data_file7.pkl"
```

### Load Report From Salesforce

```python
# File 1 - getting from a Gconnector sheet due to an error with normal salesforce import

file_1 = Spread('1r3YGO2PMz7tVu3duCN1stQG_phFFKOjW0KZO9XKgoP8')
file_1.open_sheet(0)
sf_df = file_1.sheet_to_df()
```

```python
# Run if downloading report from salesforce






# File 2 (As needed)
report_id_file2 = "00O1M0000077bWiUAI"
file_2_id_column = 'Incoming SMS: ID' # adjust as needed
sf_df_file2 =  sf.get_report(report_id_file2, id_column=file_2_id_column)

# File 3 (As needed)
report_id_file3 = "00O1M0000077bWTUAY"
file_3_id_column = 'SMS History: Record number' # adjust as needed
sf_df_file3 =  sf.get_report(report_id_file3, id_column=file_3_id_column)


# File 4 (As needed)
report_id_file4 = "00O1M0000077bWnUAI"
file_4_id_column = '18 Digit ID' # adjust as needed
sf_df_file4 =  sf.get_report(report_id_file4, id_column=file_4_id_column)



# File 5 (As needed)
report_id_file5 = "00O1M0000077cchUAA"
file_5_id_column = '18 Digit ID' # adjust as needed
sf_df_file5 =  sf.get_report(report_id_file5)


# # File 6 (As needed)
report_id_file6 = "00O1M0000077bbYUAQ"
file_6_id_column = 'Workshop Session Attendance: Workshop Session Attendance Name' # adjust as needed
sf_df_file6 =  sf.get_report(report_id_file6, id_column=file_6_id_column)

# #File 7
report_id_file7 = "00O1M0000077c3cUAA"
file_7_id_column = 'Case Note: Case Note ID' # adjust as needed
sf_df_file7 =  sf.get_report(report_id_file7, id_column=file_7_id_column)



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
```

```python
# Combined Spanish and English HS Surveys
df_spanish.columns = df_english.columns
df_combined = pd.concat([df_english, df_spanish, df_english_second_sheet], axis=0, ignore_index=True)

# Combine Old College Responses (old meaning before connected to Google Sheets and the new responses)
df_college = pd.concat([df_college_old, df_college_new], axis=0, ignore_index=True)
```

```python
df_combined['Submitted Date'] = pd.to_datetime(df_combined['Submitted Date'])
df_combined.rename(columns={'Submitted Date': "Date"}, inplace=True)


df_college['Submitted Date'] = pd.to_datetime(df_college['Submitted Date'])
df_college.rename(columns={'Submitted Date': "Date"}, inplace=True)
```

#### Save report as CSV

```python
len(sf_df), len(sf_df_file2),len(sf_df_file3),len(sf_df_file4)
```

```python
# # File 1
sf_df.to_csv(in_file1, index=True)
```

```python
# # Only run if ran above cell



# # File 2 and 3 (As needed)
sf_df_file2.to_csv(in_file2, index=False)
sf_df_file3.to_csv(in_file3, index=False)
sf_df_file4.to_csv(in_file4, index=False)
sf_df_file5.to_csv(in_file5, index=False)
sf_df_file6.to_csv(in_file6, index=False)
sf_df_file7.to_csv(in_file7, index=False)


```

### Load DF from saved CSV
* Start here if CSV already exist 

```python
# ALWAYS RUN 
# Data Frame for File 1 - if using more than one file, rename df to df_file1
df = pd.read_csv(in_file1)


# Data Frames for File 1 and 2 (As needed)

df_file2 = pd.read_csv(in_file2)
df_file3 = pd.read_csv(in_file3)
df_file4 = pd.read_csv(in_file4)
df_file5 = pd.read_csv(in_file5)
df_file6 = pd.read_csv(in_file6)
df_file7 = pd.read_csv(in_file7)
```

```python
df_file5['Scholarship Application: Date Applied'] = pd.to_datetime(df_file5['Scholarship Application: Date Applied'])

df_file5['Date'] = pd.to_datetime(df_file5['Date'])
# df_file5.rename(columns={'Scholarship Application: Date Applied': "Date"}, inplace=True)
# df_file5.rename(columns={'Scholarship Application: Date Applied': "Date"}, inplace=True)
```

```python
df['Date']= pd.to_datetime(df['Date'])

df_file2['Incoming SMS: Created Date'] = pd.to_datetime(df_file2['Incoming SMS: Created Date'])
df_file2.rename(columns={'Incoming SMS: Created Date': "Date"}, inplace=True)

df_file3['SMS History: Created Date'] = pd.to_datetime(df_file3['SMS History: Created Date'])
df_file3.rename(columns={'SMS History: Created Date': "Date"}, inplace=True)

df_file6['Date']= pd.to_datetime(df_file6['Date'])
df_file7['Date']= pd.to_datetime(df_file7['Date'])


```

```python
df_reciprocal_activity = df[df['Reciprocal Communication'] > 0]
```

```python
def create_df_to_merge_day(df, col_id, col_name, day_limit=None):

    if day_limit:
        _df = df[df.Date >= (datetime.now() - timedelta(days=day_limit))]

    _series = _df.groupby(col_id).size()
    if day_limit:
        _series.name = col_name + "_" + str(day_limit) + "_day"
    else:
        _series.name = col_name
    _series.index.names = ['18 Digit ID']
    _series = _series.to_frame().reset_index()
    return _series


def create_df_to_merge(df, col_id, col_name):
    _series = df.groupby(col_id).size()
    _series.name = col_name
    _series.index.names = ['18 Digit ID']

    _series = _series.to_frame().reset_index()

    return _series
```

```python
create_df_to_merge_day(df_file6, "18 Digit ID", 'workshops_attended', 7).sum()
```

```python
list_of_frames_to_merge = []


# 7 Day Counts
day_adjust = 7 
list_of_frames_to_merge.append(create_df_to_merge_day(df, '18 Digit ID', 'activity_count', day_adjust))
list_of_frames_to_merge.append(create_df_to_merge_day(df_file2, 'Contact: 18 Digit ID', 'incoming_sms_count', day_adjust))
list_of_frames_to_merge.append(create_df_to_merge_day(df_file3, 'Contact: 18 Digit ID', 'outgoing_sms_count', day_adjust))
list_of_frames_to_merge.append(create_df_to_merge_day(df_reciprocal_activity, '18 Digit ID', 'reciprocal_count', day_adjust))
workshops_7_day = df_file6[df_file6.Date >= datetime.now() - timedelta(days=day_adjust)]['18 Digit ID'].value_counts().to_frame().reset_index()
workshops_7_day.rename(columns = {'index':'18 Digit ID', "18 Digit ID": "workshops_attendend_7_days"}, inplace = True) 
list_of_frames_to_merge.append(workshops_7_day)
list_of_frames_to_merge.append(create_df_to_merge_day(df_file7, 'Academic Term: 18 Digit Student ID', 'case_note_count', day_adjust))


# 30 Day
day_adjust = 30
list_of_frames_to_merge.append(create_df_to_merge_day(df, '18 Digit ID', 'activity_count', day_adjust))
list_of_frames_to_merge.append(create_df_to_merge_day(df_file2, 'Contact: 18 Digit ID', 'incoming_sms_count', day_adjust))
list_of_frames_to_merge.append(create_df_to_merge_day(df_file3, 'Contact: 18 Digit ID', 'outgoing_sms_count', day_adjust))
list_of_frames_to_merge.append(create_df_to_merge_day(df_reciprocal_activity, '18 Digit ID', 'reciprocal_count', day_adjust))
workshops_30_day = df_file6[df_file6.Date >= datetime.now() - timedelta(days=day_adjust)]['18 Digit ID'].value_counts().to_frame().reset_index()
workshops_30_day.rename(columns = {'index':'18 Digit ID', "18 Digit ID": "workshops_attendend_30_days"}, inplace = True) 
list_of_frames_to_merge.append(workshops_30_day)
list_of_frames_to_merge.append(create_df_to_merge_day(df_file7, 'Academic Term: 18 Digit Student ID', 'case_note_count', day_adjust))

# All Time 
list_of_frames_to_merge.append(create_df_to_merge(df, '18 Digit ID', 'activity_count'))
list_of_frames_to_merge.append(create_df_to_merge(df_file2, 'Contact: 18 Digit ID', 'incoming_sms_count'))
list_of_frames_to_merge.append(create_df_to_merge(df_file3, 'Contact: 18 Digit ID', 'outgoing_sms_count'))
list_of_frames_to_merge.append(create_df_to_merge(df_reciprocal_activity, '18 Digit ID', 'reciprocal_count'))
attended_workshops = df_file6['18 Digit ID'].value_counts().to_frame().reset_index()
attended_workshops.rename(columns = {'index':'18 Digit ID', "18 Digit ID": "workshops_attendend"}, inplace = True) 
list_of_frames_to_merge.append(attended_workshops)
list_of_frames_to_merge.append(create_df_to_merge(df_file7, 'Academic Term: 18 Digit Student ID', 'case_note_count'))




```

```python
for frame in list_of_frames_to_merge:
    df_file4 = df_file4.merge(frame, how='left',
                          on='18 Digit ID')
```

```python
df_combined_last_7 = df_combined[(df_combined['Date'] >= (datetime.now() - timedelta(days=7)))]
```

```python
# Total
took_hs_survey = list(df_combined['Student: High School Contact Id'])
took_college_survey = list(df_college['Student 18 Digit Id'])
took_survey = took_college_survey + took_hs_survey


# 7 Days

df_combined_last_7 = df_combined[(df_combined['Date'] >= (datetime.now() - timedelta(days=7)))]
df_college_last_7 = df_college[(df_college['Date'] >= (datetime.now() - timedelta(days=7)))]

took_hs_survey_7_days = list(df_combined_last_7['Student: High School Contact Id'])
took_college_survey_7_days = list(df_college_last_7['Student 18 Digit Id'])
took_survey_last_7_days = took_college_survey_7_days + took_hs_survey_7_days


# 30 Days


df_combined_last_30 = df_combined[(df_combined['Date'] >= (datetime.now() - timedelta(days=30)))]
df_college_last_30 = df_college[(df_college['Date'] >= (datetime.now() - timedelta(days=30)))]
took_hs_survey_30_days = list(df_combined_last_30['Student: High School Contact Id'])
took_college_survey_30_days = list(df_college_last_30['Student 18 Digit Id'])
took_survey_last_30_days = took_college_survey_30_days + took_hs_survey_30_days

```

```python
df_file5_7_days = df_file5[df_file5.Date >= (datetime.now() - timedelta(days=7))]
emergency_fund_7_days = df_file5_7_days.groupby('18 Digit ID').sum()
for column in emergency_fund_7_days:
    emergency_fund_7_days.rename(columns={column:column+"_7_days"}, inplace=True)
    
emergency_fund_7_days = emergency_fund_7_days.reset_index()
```

```python
df_file5_30_days = df_file5[df_file5.Date >= (datetime.now() - timedelta(days=30))]
emergency_fund_30_days = df_file5_30_days.groupby('18 Digit ID').sum()
for column in emergency_fund_30_days:
    emergency_fund_30_days.rename(columns={column:column+"_30_days"}, inplace=True)
    
emergency_fund_30_days = emergency_fund_30_days.reset_index()

```

```python
emergency_fund_total = df_file5.groupby('18 Digit ID').sum().reset_index()



```

```python
df_file4 = df_file4.merge(emergency_fund_total, how='left',
                          on='18 Digit ID')
```

```python
df_file4 = df_file4.merge(emergency_fund_7_days, how='left',
                          on='18 Digit ID')
```

```python
df_file4 = df_file4.merge(emergency_fund_30_days, how='left',
                          on='18 Digit ID')
```

```python
df_file4['took_survey'] = df_file4['18 Digit ID'].isin(took_survey)

df_file4['took_survey_7_days'] = df_file4['18 Digit ID'].isin(took_survey_last_7_days)

df_file4['took_survey_30_days'] = df_file4['18 Digit ID'].isin(took_survey_last_30_days)

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
