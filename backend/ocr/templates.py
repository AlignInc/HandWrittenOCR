"""
Form templates define the structure and fields to extract from different form types.
"""

# GCCF 10K Application Form - Page 1
GCCF_10K_P1_TEMPLATE = {
    "form_name": "GCCF 10K Application Form (Page 1)",
    "fields": [
        # Header
        {"key": "header_district", "label": "區", "type": "text"},
        {"key": "header_number", "label": "編號", "type": "text"},
        {"key": "header_date", "label": "日期", "type": "text"},
        # Applicant
        {"key": "applicant_name_en", "label": "英文姓名", "type": "text"},
        {"key": "applicant_name_zh", "label": "中文姓名", "type": "text"},
        {"key": "applicant_sex", "label": "性別", "type": "text"},
        {"key": "applicant_age", "label": "年齡", "type": "text"},
        {"key": "applicant_hkid", "label": "香港身分證號碼", "type": "text"},
        {"key": "applicant_race_chinese", "label": "族裔", "type": "text"},
        {"key": "applicant_tel", "label": "電話", "type": "text"},
        # Employment
        {"key": "employment_post", "label": "職位", "type": "text"},
        {"key": "employment_monthly_salary", "label": "月薪", "type": "text"},
        {"key": "employment_other_income", "label": "其他入息", "type": "text"},
        {"key": "employment_unemployed_reason", "label": "如並無就業", "type": "text"},
        # Address
        {"key": "address_detail", "label": "住址", "type": "text"},
        {"key": "address_monthly_rental", "label": "月租", "type": "text"},
        # Family members table anchor
        {"key": "family_table", "label": "申請人家屬", "type": "table"},
        {"key": "family_bottom_question", "label": "是否曾向華人慈善基金申請", "type": "text"},
    ],
    "gpt_prompt": """你是一個專業的香港表格識別助手。這是GCCF 10K申請表第1頁，請提取頭部、申請人資料、現職、住址、家屬表格中的資料，並以提供的key返回JSON。"""
}

# GCCF 10K Application Form - Page 2
GCCF_10K_P2_TEMPLATE = {
    "form_name": "GCCF 10K Application Form (Page 2)",
    "fields": [
        {"key": "incident_description", "label": "申請援助金的事故及理由", "type": "text"},
        {"key": "amount_applied", "label": "申請金額", "type": "text"},
        {"key": "signature_applicant", "label": "申請人簽署", "type": "text"},
        {"key": "date_applicant", "label": "日期", "type": "text"},
        {"key": "signature_officer", "label": "調查人員簽署", "type": "text"},
        {"key": "name_officer", "label": "姓名", "type": "text"},
        {"key": "post_officer", "label": "職位", "type": "text"},
        {"key": "date_officer", "label": "日期", "type": "text"},
    ],
    "gpt_prompt": """你是一個專業的香港表格識別助手。這是GCCF 10K申請表第2頁，請提取事故描述、申請金額以及簽署區域的欄位。"""
}

# Estate Roster / Management Book (A01)
ROSTER_TEMPLATE = {
    "form_name": "Estate Owner Roster",
    "fields": [
        {"key": "roster_rows", "label": "單位", "type": "table"},  # expect a list of rows with unit, owner_name, home_phone, office_phone, mobile_phone
        {"key": "roster_footer_note", "label": "聯絡電話", "type": "text"},
    ],
    "gpt_prompt": """這是一張住戶/業主任名冊（A01）。請輸出JSON：
{
  "data": {
    "roster_rows": [
      {"unit": "A101", "owner_name": "...", "home_phone": "...", "office_phone": "...", "mobile_phone": "..."},
      ...
    ],
    "roster_footer_note": "..."
  },
  "confidence": { "roster_rows": 0.6, "roster_footer_note": 0.5 }
}
單位號碼請根據影像內的預印或手寫內容識別，不要預填。若某欄空白請用 null。"""
}

# Template registry
FORM_TEMPLATES = {
    "GCCF_10K_P1": GCCF_10K_P1_TEMPLATE,
    "GCCF_10K_P2": GCCF_10K_P2_TEMPLATE,
    "MGT_BOOK": ROSTER_TEMPLATE,
    "HOUSE_ROSTER": ROSTER_TEMPLATE,
}

def get_template(form_type: str):
    """Get form template by type"""
    return FORM_TEMPLATES.get(form_type, GCCF_10K_P1_TEMPLATE)

def get_field_labels(form_type: str):
    """Get field labels for display"""
    template = get_template(form_type)
    return {field["key"]: field["label"] for field in template["fields"]}
