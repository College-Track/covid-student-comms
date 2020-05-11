import pandas as pd
from datetime import datetime, timedelta


def group_by_date(file, student_id, files):
    _df = files = files[file].df.groupby([student_id, "Date"]).size()

    _df.rename_axis(["18 Digit ID", "Date"], inplace=True)

    return _df


def create_list_of_counts(files):

    recip_activity_count = group_by_date("reciprocal_activities", "18 Digit ID", files)
    incoming_sms_count = group_by_date("incoming_sms", "Contact: 18 Digit ID", files)
    survey_count = group_by_date("survey", "18 Digit ID", files)
    case_note_count = group_by_date(
        "case_notes", "Academic Term: 18 Digit Student ID", files
    )
    workshops_count = group_by_date("workshops", "18 Digit ID", files)

    list_of_counts = [
        recip_activity_count,
        incoming_sms_count,
        case_note_count,
        survey_count,
        workshops_count,
    ]

    return list_of_counts


def create_total_counts(list_of_counts):
    _count = list_of_counts[0].add(list_of_counts[1], fill_value=0)

    for grouping in list_of_counts[2:]:
        _count = _count.add(grouping, fill_value=0)

    _count = pd.DataFrame(_count)
    _count.reset_index(inplace=True)
    _count.rename(columns={0: "Count"}, inplace=True)
    return _count


def create_timedelta(date):
    # If Sunday, advance to monday
    if date.strftime("w%") == 0:
        return timedelta(days=-1)
    # If Monday - Saturday go back to Monday
    else:
        day_adjust = int(date.strftime("%w"))
        return timedelta(days=day_adjust - 1)


def adjust_count_dates(_count):

    _count["Date"] = pd.to_datetime(_count["Date"])
    _count["adjust"] = _count.apply(lambda x: create_timedelta(x["Date"]), axis=1)
    _count["Date"] = _count["Date"] - pd.TimedeltaIndex(_count.adjust, unit="d")
    _count.drop(columns="adjust", inplace=True)
    return _count


def create_roster_with_counts(_roster, _count):
    _roster_count = _roster.merge(_count, on="18 Digit ID", how="left")
    _roster_count["Date"] = _roster_count["Date"].dt.date
    _roster_count = _roster_count[_roster_count["Count"] > 0]

    return _roster_count


def create_site_count(_roster_count):
    site_count = _roster_count.groupby(
        ["Site", "High School Class", "Contact Record Type", "Date"]
    )["18 Digit ID"].nunique()
    site_count = pd.DataFrame(site_count).reset_index()
    site_count.rename(columns={"18 Digit ID": "Number of Students"}, inplace=True)

    site_count["Date"] = pd.to_datetime(site_count["Date"])

    return site_count


def create_site_count_with_enrollments(_roster, site_count):
    roster_enrollment_count = (
        _roster.groupby(["Site", "High School Class", "Contact Record Type"])
        .size()
        .reset_index()
    )
    roster_enrollment_count.rename(
        columns={0: "Number of Enrolled Students"}, inplace=True
    )

    site_count_with_enrollments = site_count.merge(
        roster_enrollment_count,
        on=["Site", "High School Class", "Contact Record Type"],
        how="left",
    )

    site_count_with_enrollments["Date"] = pd.to_datetime(
        site_count_with_enrollments["Date"]
    )

    site_count_with_enrollments = site_count_with_enrollments[
        site_count_with_enrollments["Date"] >= datetime(2020, 3, 1)
    ]
    site_count_with_enrollments = site_count_with_enrollments[
        site_count_with_enrollments["Date"] <= datetime.now()
    ]

    return site_count_with_enrollments


def generate_summary_frames(files):
    days_to_check = [7, 30, None]

    for file in files:
        if file == "roster":
            continue

        for day_limit in days_to_check:
            if file == "emergency_fund":
                files[file].create_summary(day_limit, sum_type="sum")
            else:
                files[file].create_summary(day_limit)


def prep_master_df_with_counts(files, master_df):

    for file in files:
        if file == "roster":
            continue
        master_df = master_df.merge(
            files[file].seven_day_summary, how="left", left_index=True, right_index=True
        )
        master_df = master_df.merge(
            files[file].thirty_day_summary,
            how="left",
            left_index=True,
            right_index=True,
        )
        master_df = master_df.merge(
            files[file].all_time_summary, how="left", left_index=True, right_index=True
        )
    return master_df


def count_of_key_areas(master_df, threshold_frames):
    time_periods = ["", "_7_days", "_30_days"]

    for key, items in threshold_frames.items():

        for time_period_name in time_periods:
            master_df["total_" + key + time_period_name] = 0
            for item in items:
                master_df_column = "total_" + key + time_period_name
                sub_column = item + time_period_name
                master_df[master_df_column] = master_df[master_df_column].add(
                    master_df[sub_column], fill_value=0
                )

    return master_df


def determine_if_met_threshold(master_df, threshold_frames):
    time_periods = ["", "_7_days", "_30_days"]

    for key in threshold_frames.keys():
        for time_period_name in time_periods:
            column_name = "met_" + key + time_period_name
            check_column = "total_" + key + time_period_name

            master_df[column_name] = master_df[check_column] > 0

    return master_df


def create_table_for_report(
    df,
    percent_column,
    count_column,
    time_period,
    measure,
    include_ps=True,
    workshop=False,
):
    if time_period == "":
        time_period_text = "Since March 1st"
    else:
        time_period_text = str(time_period) + " Days"

    hs_df = df[df["Contact Record Type"] == "Student: High School"]
    count_table_hs = pd.pivot_table(
        data=hs_df, index="Site", values=count_column, aggfunc="sum", margins=False
    )
    percent_table_hs = pd.crosstab(
        hs_df["Site"], hs_df[percent_column], normalize=False, margins=False
    )

    student_count_hs = pd.DataFrame(hs_df["Site"].value_counts()).rename(
        columns={"Site": "Student Count"}
    )

    if workshop == True:
        count_table_hs.rename(
            columns={count_column: "Count of Workshop Sessions"}, inplace=False
        )

    count_table_hs.rename(columns={count_column: "Count of " + measure}, inplace=True)

    percent_table_hs = percent_table_hs.drop(columns=False)
    percent_table_hs.rename(
        columns={True: "Numerator of Site's Students " + measure}, inplace=True
    )
    table_hs = pd.concat([count_table_hs, percent_table_hs], axis=1, sort=True)
    table_hs["Numerator of Site's Students " + measure] = table_hs[
        "Numerator of Site's Students " + measure
    ]
    table_hs["record_type"] = "High School"
    table_hs["time_period"] = time_period_text

    table_hs = pd.concat([table_hs, student_count_hs], axis=1, sort=True).reset_index()

    if include_ps == True:
        college_df = df[df["Contact Record Type"] == "Student: Post-Secondary"]
        count_table_ps = pd.pivot_table(
            data=college_df,
            index="Site",
            values=count_column,
            aggfunc="sum",
            margins=False,
        )
        percent_table_ps = pd.crosstab(
            college_df["Site"],
            college_df[percent_column],
            normalize=False,
            margins=False,
        )
        count_table_ps.rename(
            columns={count_column: "Count of " + measure}, inplace=True
        )
        percent_table_ps = percent_table_ps.drop(columns=False)
        percent_table_ps.rename(
            columns={True: "Numerator of Site's Students " + measure}, inplace=True
        )
        table_college = pd.concat([count_table_ps, percent_table_ps], axis=1, sort=True)
        #         table_college["Numerator of Site's Students " + measure] = (
        #             table_college["Numerator of Site's Students " + measure])
        table_college["record_type"] = "Post-Secondary"
        table_college["time_period"] = time_period_text

        student_count_college = pd.DataFrame(college_df["Site"].value_counts()).rename(
            columns={"Site": "Student Count"}
        )
        table_college = pd.concat(
            [table_college, student_count_college], axis=1, sort=True
        ).reset_index()

        return table_hs.append(table_college)
    else:

        return table_hs


def create_summary_tables(df):
    time_periods = ["", 7, 30]
    merge_columns = ["index", "record_type", "time_period", "Student Count"]
    _complete_table = pd.DataFrame()
    for time_period in time_periods:
        if time_period != "":
            column_text = "_" + str(time_period) + "_days"
        else:
            column_text = ""
        _outreach_table = create_table_for_report(
            df,
            "met_outreach" + column_text,
            "total_outreach" + column_text,
            time_period,
            "all_contacts",
        )

        _outreach_minus_text = create_table_for_report(
            df,
            "met_outreach_minus_text" + column_text,
            "total_outreach_minus_text" + column_text,
            time_period,
            "all_contacts_no_text",
        )

        _reciprocal_communication_table = create_table_for_report(
            df,
            "met_reciprocal" + column_text,
            "total_reciprocal" + column_text,
            time_period,
            "reciprocal_communication",
        )

        _workshop_table = create_table_for_report(
            df,
            "met_workshop" + column_text,
            "workshop_count" + column_text,
            time_period,
            "workshops",
            include_ps=False,
            workshop=True,
        )

        _table = _outreach_table.merge(_outreach_minus_text, on=merge_columns)

        _table = _table.merge(_reciprocal_communication_table, on=merge_columns)

        _table = _table.merge(_workshop_table, on=merge_columns, how="outer")

        _complete_table = _complete_table.append(_table)

    return _complete_table


def append_region(site, regions):
    for region, sites in regions.items():
        if site in sites:
            return region
        else:
            continue
