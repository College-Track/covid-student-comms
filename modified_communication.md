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
import helpers

# warnings.filterwarnings('ignore')

```

```python
%matplotlib inline

```

### File Locations

```python
today = datetime.today()
in_file = Path.cwd() / "data" / "processed" / "processed_data.pkl"
report_dir = Path.cwd() / "reports"
report_file = report_dir / "Excel_Analysis_{today:%b-%d-%Y}.xlsx"
```

```python
df = pd.read_pickle(in_file)
```

### Perform Data Analysis

```python
def create_table_for_report(df, percent_column, count_column, time_period, measure, include_ps=True, workshop=False):
    if time_period == "all":
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
    df, "been_contacted", 'total_contacts', "all", 'all_contacts')


been_contacted_no_text = create_table_for_report(
    df, 'been_contacted_minis_text', "activity_count", "all", 'all_contacts_no_text')


reciprocal_communication_table = create_table_for_report(
    df, 'reciprocal_communication', "total_reciprocal_communication", "all", 'reciprocal_communication')


attended_workshop_table = create_table_for_report(
    df, 'attended_at_least_one_workshop', "workshops_attendend", "all", 'workshops',include_ps=False, workshop=True)
```

```python
merge_columns = ['index', 'record_type', 'time_period', 'Student Count']
all_time = been_contacted_table.merge(been_contacted_no_text, on=merge_columns).merge(
    reciprocal_communication_table, on=merge_columns).merge(attended_workshop_table, on =merge_columns, how='outer')
```

```python
# 7 Days 

been_contacted_table_7_days = create_table_for_report(
    df, "been_contacted_7_days", 'total_contacts_7_days', 7, 'all_contacts')

been_contacted_no_text_table_7_days = create_table_for_report(
    df, 'been_contacted_minis_text_7_days', "activity_count_7_day", 7, 'all_contacts_no_text')

reciprocal_communication_table_7_day= create_table_for_report(
    df, 'reciprocal_communication_7_days', "total_reciprocal_communication_7_days", 7, 'reciprocal_communication')

attended_workshop_table_7_days = create_table_for_report(
    df, 'attended_at_least_one_workshop_7_days', "workshops_attendend_7_days", 7, 'workshops', include_ps=False, workshop=True)

```

```python
seven_days = been_contacted_table_7_days.merge(been_contacted_no_text_table_7_days, on=merge_columns).merge(
    reciprocal_communication_table_7_day, on=merge_columns).merge(attended_workshop_table_7_days, on=merge_columns, how='outer')
```

```python
table = seven_days.append(all_time)
```

```python
# 30 Days

been_contacted_table_30_days = create_table_for_report(
    df, "been_contacted_30_days", 'total_contacts_30_days', 30, 'all_contacts')

been_contacted_no_text_table_30_days = create_table_for_report(
    df, 'been_contacted_minis_text_30_days', "activity_count_30_day", 30, 'all_contacts_no_text')

reciprocal_communication_table_30_day = create_table_for_report(
    df, 'reciprocal_communication_30_days', "total_reciprocal_communication_30_days", 30, 'reciprocal_communication')

attended_workshop_table_30_days = create_table_for_report(
    df, 'attended_at_least_one_workshop_30_days', "workshops_attendend_30_days", 30, 'workshops', include_ps=False,workshop=True)

```

```python
thirty_days = been_contacted_table_30_days.merge(been_contacted_no_text_table_30_days, on=merge_columns).merge(
    reciprocal_communication_table_30_day, on=merge_columns).merge(attended_workshop_table_30_days, on=merge_columns, how='outer')
```

```python
table = seven_days.append(all_time).append(thirty_days)

table.rename(columns={'index': 'Site'},inplace=True)
```

```python
table = helpers.shorten_site_names(table)

```

```python
table
```

```python
google_sheet = Spread('1tEzcIDba-dF0M4uMHUt2fwOAtO91U8q6TUFPBp9TSbY')


google_sheet.df_to_sheet(table, index=False, sheet='Aggregate Data', start='A1', replace=True)



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
