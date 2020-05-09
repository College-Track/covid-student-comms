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

This notebook contains basic statistical analysis and visualization of the data.

### Data Sources
- summary : Processed file from notebook 1-Data_Prep

### Changes
- 04-05-2020 : Started project

```python
import pandas as pd
from pathlib import Path
from datetime import datetime,timedelta
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
from gspread_pandas import Spread, Client
# warnings.filterwarnings('ignore')

```

```python
%matplotlib inline

```

### File Locations

```python
today = datetime.today()
in_file = Path.cwd() / "data" / "processed" / "summary_file.pkl"
report_dir = Path.cwd() / "reports"
report_file = report_dir / "Excel_Analysis_{today:%b-%d-%Y}.xlsx"
```

```python
df = pd.read_pickle(in_file)
```

### Perform Data Analysis

```python
def create_table_for_report(df, percent_column, count_column, include_ps=True, workshop=False):

    hs_df = df[df['Contact Record Type'] == "Student: High School"]
    count_table_hs = pd.pivot_table(
        data=hs_df, index='Site', values=count_column, aggfunc='sum', margins=True)
    percent_table_hs = pd.crosstab(
        hs_df['Site'], hs_df[percent_column], normalize='index', margins=True)
    if workshop == True:
        count_table_hs.rename(
            columns={count_column: "Count of Workshop Sessions"}, inplace=True)

    count_table_hs.rename(
        columns={count_column: "Count of Interactions"}, inplace=True)

    percent_table_hs = percent_table_hs.drop(columns=False)
    percent_table_hs.rename(
        columns={True: "Percent of Site's Students"}, inplace=True)
    table_hs = pd.concat([count_table_hs, percent_table_hs], axis=1)
    table_hs["Percent of Site's Students"] = (
        table_hs["Percent of Site's Students"].round(2) * 100).astype(int).astype(str) + '%'

    if include_ps == True:
        college_df = df[df['Contact Record Type'] == "Student: Post-Secondary"]
        count_table_ps = pd.pivot_table(
            data=college_df, index='Site', values=count_column, aggfunc='sum', margins=True)
        percent_table_ps = pd.crosstab(
            college_df['Site'], college_df[percent_column], normalize='index', margins=True)
        count_table_ps.rename(
            columns={count_column: "Count of Interactions"}, inplace=True)
        percent_table_ps = percent_table_ps.drop(columns=False)
        percent_table_ps.rename(
            columns={True: "Percent of Site's Students"}, inplace=True)
        table_college = pd.concat([count_table_ps, percent_table_ps], axis=1)
        table_college["Percent of Site's Students"] = (
            table_college["Percent of Site's Students"].round(2) * 100).astype(str) + '%'
        return table_hs, table_college
    else:

        return table_hs
```

```python
df.columns
```

```python
# All Time

been_contacted_table_hs, been_contacted_table_college = create_table_for_report(
    df, "met_outreach", 'total_outreach')

been_contacted_no_text_table_hs, been_contacted_no_text_table_college = create_table_for_report(
    df, 'met_outreach_minus_text', "total_outreach_minus_text")

reciprocal_communication_table_hs, reciprocal_communication_table_college = create_table_for_report(
    df, 'met_reciprocal', "total_reciprocal")

attended_workshop_table_hs = create_table_for_report(
    df, 'met_workshop', "total_workshop", include_ps=False, workshop=True)
```

```python
# merge_columns = ['Site', 'record_type', 'time_period']
# all_time = been_contacted_table.merge(been_contacted_no_text, on=merge_columns).merge(
#     reciprocal_communication_table, on=merge_columns).merge(attended_workshop_table, on =merge_columns, how='outer')
```

```python
# 7 Days 

been_contacted_table_7_days_hs, been_contacted_table_7_days_college = create_table_for_report(
    df, "met_outreach_7_days", 'total_outreach_7_days')

been_contacted_no_text_table_7_days_hs, been_contacted_no_text_table_7_days_college = create_table_for_report(
    df, 'met_outreach_minus_text_7_days', "total_outreach_minus_text_7_days")

reciprocal_communication_table_7_days_hs, reciprocal_communication_table_7_days_college = create_table_for_report(
    df, 'met_reciprocal_7_days', "total_reciprocal_7_days")

attended_workshop_table_7_days_hs = create_table_for_report(
    df, 'met_workshop_7_days', "total_workshop_7_days", include_ps=False, workshop=True)
```

```python
# # seven_days = been_contacted_table_7_days.merge(been_contacted_no_text_table_7_days, on=merge_columns).merge(
#     reciprocal_communication_table_7_day, on=merge_columns).merge(attended_workshop_table_7_days, on=merge_columns, how='outer')
```

```python
# table = seven_days.append(all_time)
```

```python
# 30 Days

been_contacted_table_30_days_hs, been_contacted_table_30_days_college = create_table_for_report(
    df, "met_outreach_30_days", 'total_outreach_30_days')

been_contacted_no_text_table_30_days_hs, been_contacted_no_text_table_30_days_college = create_table_for_report(
    df, 'met_outreach_minus_text_30_days', "total_outreach_minus_text_30_days")

reciprocal_communication_table_30_days_hs, reciprocal_communication_table_30_days_college = create_table_for_report(
    df, 'met_reciprocal_30_days', "total_reciprocal_30_days")

attended_workshop_table_30_days_hs = create_table_for_report(
    df, 'met_workshop_30_days', "total_workshop_30_days", include_ps=False,workshop=True)
```

```python
seven_day_contacts = reciprocal_communication_table_hs.append(reciprocal_communication_table_college)
```

```python
# # 30 Days

# been_contacted_table_30_days_hs, been_contacted_table_30_days_college = create_table_for_report(
#     df, "been_contacted_30_days", 'total_contacts_30_days', 30)

# been_contacted_no_text_table_30_days_hs, been_contacted_no_text_table_30_days_college = create_table_for_report(
#     df, 'been_contacted_minis_text_30_days', "activity_count_30_day", 30)

# reciprocal_communication_table_30_days_hs, reciprocal_communication_table_30_days_college = create_table_for_report(
#     df, 'reciprocal_communication_30_days', "total_reciprocal_communication_30_days", 30)

# attended_workshop_table_30_days_hs = create_table_for_report(
#     df, 'attended_at_least_one_workshop_30_days', "workshops_attendend_30_days", 30, include_ps=False,workshop=True)

```

```python
# been_contacted_table_30_days_college.merge(been_contacted_table_30_days_hs, on=['Site', 'record_type', 'time_period'], how='outer')
```

```python
emergency_funds = df.pivot_table(index='Site', values=['amount'], aggfunc='sum', margins=True)
```

```python
emergency_funds_30_days = df.pivot_table(index='Site', values=[
    'amount_30_days'], aggfunc='sum', margins=True)
```

```python
emergency_funds_7_days = df.pivot_table(index='Site', values=[
    'amount_7_days'], aggfunc='sum', margins=True)
```

```python
sites_to_remove = ['College Track Denver', 'College Track Ward 8', 'College Track at The Durant Center']

emergency_funds_7_days = emergency_funds_7_days[~(emergency_funds_7_days.index.isin(sites_to_remove))]

emergency_funds_30_days = emergency_funds_30_days[~(emergency_funds_30_days.index.isin(sites_to_remove))]

emergency_funds = emergency_funds[~(emergency_funds.index.isin(sites_to_remove))]
```

```python
test_sheet = '1N6RrEwQQA7FsjDxr482zbpkqqgV7Zj_paN8WtVVUZls'

google_sheet = Spread("1CsDG8bz9ZpkkruXN-RA2Zdrl5dPC21LlcFOAgb3qHlA")

google_sheet.open_sheet(0)


```

```python
update_date = datetime.now().date().strftime("%m/%d/%Y")
```

```python
# All Time - HS

google_sheet.df_to_sheet(been_contacted_table_hs, index=True,
                         sheet='HS - Since March 1', start='A2', replace=False)

google_sheet.df_to_sheet(been_contacted_no_text_table_hs, index=True,
                         sheet='HS - Since March 1', start='A20', replace=False)

google_sheet.df_to_sheet(reciprocal_communication_table_hs, index=True,
                         sheet='HS - Since March 1', start='E2', replace=False)

google_sheet.df_to_sheet(attended_workshop_table_hs, index=True,
                         sheet='HS - Since March 1', start='E20', replace=False)

google_sheet.update_cells(start='A34',end="A35", sheet="HS - Since March 1", vals=[
                          'Updated:', update_date])


# 30 Days - HS

data_from = (datetime.now().date() - timedelta(days=30)).strftime("%m/%d/%Y")

google_sheet.df_to_sheet(been_contacted_table_30_days_hs, index=True,
                         sheet='HS - Last 30 Days', start='A2', replace=False)

google_sheet.df_to_sheet(been_contacted_no_text_table_30_days_hs,
                         index=True, sheet='HS - Last 30 Days', start='A20', replace=False)

google_sheet.df_to_sheet(reciprocal_communication_table_30_days_hs,
                         index=True, sheet='HS - Last 30 Days', start='E2', replace=False)

google_sheet.df_to_sheet(attended_workshop_table_30_days_hs,
                         index=True, sheet='HS - Last 30 Days', start='E20', replace=False)

google_sheet.update_cells(start='A34',end="A37", sheet="HS - Last 30 Days", vals=[
                          'Updated:', update_date, 'Containing Data Since:', data_from])


# 7 Days - HS
data_from = (datetime.now().date() - timedelta(days=7)).strftime("%m/%d/%Y")


google_sheet.df_to_sheet(been_contacted_table_7_days_hs, index=True,
                         sheet='HS - Last 7 Days', start='A2', replace=False)

google_sheet.df_to_sheet(been_contacted_no_text_table_7_days_hs,
                         index=True, sheet='HS - Last 7 Days', start='A20', replace=False)

google_sheet.df_to_sheet(reciprocal_communication_table_7_days_hs,
                         index=True, sheet='HS - Last 7 Days', start='E2', replace=False)

google_sheet.df_to_sheet(attended_workshop_table_7_days_hs,
                         index=True, sheet='HS - Last 7 Days', start='E20', replace=False)


google_sheet.update_cells(start='A34',end="A37", sheet="HS - Last 7 Days", vals=[
                          'Updated:', update_date, 'Containing Data Since:', data_from])
```

```python
# # All Time - College

google_sheet.df_to_sheet(been_contacted_table_college, index=True,
                         sheet='College - Since March 1', start='A2', replace=False)

google_sheet.df_to_sheet(been_contacted_no_text_table_college, index=True,
                         sheet='College - Since March 1', start='A16', replace=False)

google_sheet.df_to_sheet(reciprocal_communication_table_college, index=True,
                         sheet='College - Since March 1', start='E2', replace=False)


google_sheet.df_to_sheet(emergency_funds, index=True,
                         sheet='College - Since March 1', start='E16', replace=False)

google_sheet.update_cells(start='A28',end="A29", sheet="College - Since March 1", vals=[
                          'Updated:', update_date])


# # 30 Days - College
data_from = (datetime.now().date() - timedelta(days=30)).strftime("%m/%d/%Y")


google_sheet.df_to_sheet(been_contacted_table_30_days_college, index=True,
                         sheet='College - Last 30 Days', start='A2', replace=False)

google_sheet.df_to_sheet(been_contacted_no_text_table_30_days_college,
                         index=True, sheet='College - Last 30 Days', start='A16', replace=False)

google_sheet.df_to_sheet(reciprocal_communication_table_30_days_college,
                         index=True, sheet='College - Last 30 Days', start='E2', replace=False)

google_sheet.df_to_sheet(emergency_funds_30_days, index=True,
                         sheet='College - Last 30 Days', start='E16', replace=False)

google_sheet.update_cells(start='A28',end="A31", sheet="College - Last 30 Days", vals=[
                          'Updated:', update_date, 'Containing Data Since:', data_from])

# 7 Days - College
data_from = (datetime.now().date() - timedelta(days=7)).strftime("%m/%d/%Y")


google_sheet.df_to_sheet(been_contacted_table_7_days_college, index=True,
                         sheet='College - Last 7 Days', start='A2', replace=False)

google_sheet.df_to_sheet(been_contacted_no_text_table_7_days_college,
                         index=True, sheet='College - Last 7 Days', start='A16', replace=False)

google_sheet.df_to_sheet(reciprocal_communication_table_7_days_college,
                         index=True, sheet='College - Last 7 Days', start='E2', replace=False)

google_sheet.df_to_sheet(emergency_funds_7_days, index=True,
                         sheet='College - Last 7 Days', start='E16', replace=False)

google_sheet.update_cells(start='A28',end="A31", sheet="College - Last 7 Days", vals=[
                          'Updated:', update_date, 'Containing Data Since:', data_from])
```

```python
google_sheet.df_to_sheet(df, index=False, sheet='Raw Data', start='A1', replace=True)

```

### Save Excel file into reports directory

Save an Excel file with intermediate results into the report directory

```python
writer = pd.ExcelWriter(report_file, engine='xlsxwriter')
```

```python
df.to_excel(writer, sheet_name='Report')
```

```python
writer.save()
```
