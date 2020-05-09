files_prep = [
    {
        "name": "incoming_sms",
        "id": "00O1M0000077bWiUAI",
        "report_filter_column": "Incoming SMS: ID",
        "date_column": "Incoming SMS: Created Date",
        "summary_column_name": "incoming_sms_count",
        "student_id_column": "Contact: 18 Digit ID",
    },
    {
        "name": "emergency_fund",
        "id": "00O1M0000077cchUAA",
        "report_filter_column": "18 Digit ID",
        "date_column": "Date",
        "summary_column_name": "Amount",
        "student_id_column": "18 Digit ID",
    },
    {
        "name": "roster",
        "id": "00O1M0000077bWnUAI",
        "report_filter_column": "18 Digit ID",
        "date_column": None,
        "summary_column_name": "NA",
        "student_id_column": "NA",
    },
    {
        "name": "outgoing_sms",
        "id": "00O1M0000077bWTUAY",
        "report_filter_column": "SMS History: Record number",
        "date_column": "SMS History: Created Date",
        "summary_column_name": "outgoing_sms_count",
        "student_id_column": "Contact: 18 Digit ID",
    },
    {
        "name": "workshops",
        "id": "00O1M0000077bbYUAQ",
        "report_filter_column": "Workshop Session Attendance: Workshop Session Attendance Name",
        "date_column": "Date",
        "summary_column_name": "workshop_count",
        "student_id_column": "18 Digit ID",
    },
    {
        "name": "case_notes",
        "id": "00O1M0000077c3cUAA",
        "report_filter_column": "Case Note: Case Note ID",
        "date_column": "Date",
        "summary_column_name": "case_note_count",
        "student_id_column": "Academic Term: 18 Digit Student ID",
    },
    {
        "name": "survey",
        "id": "00O1M000007R6FrUAK",
        "report_filter_column": "18 Digit ID",
        "date_column": "Completed CT 2019-20 Survey: Date",
        "summary_column_name": "took_survey",
        "student_id_column": "18 Digit ID",
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


activities = [
    "00O1M0000077bWjUAI",
    "Activity ID",
    "activities",
    "Date",
    "activity_count",
    "18 Digit ID",
]


reciprocal_activities = [
    "00O1M0000077bWjUAI",
    "Activity ID",
    "reciprocal_activity",
    "Date",
    "reciprocal_activity_count",
    "18 Digit ID",
]


ACTIVITIES_GOOGLE_SHEET = "1r3YGO2PMz7tVu3duCN1stQG_phFFKOjW0KZO9XKgoP8"


threshold_frames = {
    "outreach": [
        "activity_count",
        "outgoing_sms_count",
        "workshop_count",
        "case_note_count",
    ],
    "outreach_minus_text": ["activity_count", "workshop_count", "case_note_count"],
    "reciprocal": [
        "incoming_sms_count",
        "reciprocal_activity_count",
        "took_survey",
        "case_note_count",
        "workshop_count",
    ],
    "workshop": ["workshop_count"],
}

regions = {
    "NOLA": ["New Orleans"],
    "NOR CAL": ["Sacramento", "Oakland", "San Francisco", "East Palo Alto"],
    "LA": ["Watts", "Boyle Heights"],
    "DC": ["Ward 8", "The Durant Center"],
    "CO": ["Denver", "Aurora"],
}


GOOGLE_SHEET_UPLOAD = "1tEzcIDba-dF0M4uMHUt2fwOAtO91U8q6TUFPBp9TSbY"

