"""
Form templates define the structure and fields to extract from different form types.
"""

# GCCF 10K Application Form Template
GCCF_10K_TEMPLATE = {
    "form_name": "GCCF 10K Application Form",
    "fields": [
        # Section 1: Applicant Information
        {"key": "applicant_name_en", "label": "申請人英文姓名", "type": "text"},
        {"key": "applicant_name_zh", "label": "申請人中文姓名", "type": "text"},
        {"key": "hkid_no", "label": "香港身份證號碼", "type": "text"},
        {"key": "date_of_birth", "label": "出生日期", "type": "date"},
        {"key": "contact_phone", "label": "聯絡電話", "type": "text"},
        {"key": "address", "label": "住址", "type": "text"},
        
        # Section 2: Employment Information
        {"key": "employment_status", "label": "就業狀況", "type": "text"},
        {"key": "employer_name", "label": "僱主名稱", "type": "text"},
        {"key": "occupation", "label": "職業", "type": "text"},
        {"key": "monthly_income", "label": "每月收入", "type": "number"},
        
        # Section 3: Family Information
        {"key": "marital_status", "label": "婚姻狀況", "type": "text"},
        {"key": "num_family_members", "label": "家庭成員人數", "type": "number"},
        {"key": "family_member_1_name", "label": "家庭成員1姓名", "type": "text"},
        {"key": "family_member_1_relation", "label": "家庭成員1關係", "type": "text"},
        {"key": "family_member_1_age", "label": "家庭成員1年齡", "type": "number"},
        {"key": "family_member_2_name", "label": "家庭成員2姓名", "type": "text"},
        {"key": "family_member_2_relation", "label": "家庭成員2關係", "type": "text"},
        {"key": "family_member_2_age", "label": "家庭成員2年齡", "type": "number"},
        
        # Section 4: Financial Information
        {"key": "monthly_rent", "label": "每月租金", "type": "number"},
        {"key": "total_assets", "label": "總資產", "type": "number"},
        {"key": "total_debts", "label": "總負債", "type": "number"},
        
        # Section 5: Application Details
        {"key": "application_amount", "label": "申請金額", "type": "number"},
        {"key": "application_purpose", "label": "申請目的", "type": "text"},
        {"key": "application_date", "label": "申請日期", "type": "date"},
        {"key": "applicant_signature", "label": "申請人簽署", "type": "text"},
    ],
    "gpt_prompt": """你是一個專業的香港表格識別助手。請從這份GCCF 10K申請表格中提取以下字段的資訊：

1. 申請人資料：英文姓名、中文姓名、香港身份證號碼、出生日期、聯絡電話、住址
2. 就業資料：就業狀況、僱主名稱、職業、每月收入
3. 家庭資料：婚姻狀況、家庭成員人數、家庭成員的姓名/關係/年齡
4. 財務資料：每月租金、總資產、總負債
5. 申請資料：申請金額、申請目的、申請日期

請以JSON格式返回，使用英文key名稱。如果某個字段無法識別，請使用null值。同時為每個字段提供0-1之間的置信度分數。

輸出格式：
{
  "data": { "applicant_name_en": "...", ... },
  "confidence": { "applicant_name_en": 0.95, ... }
}
"""
}

# Management Book Template
MGT_BOOK_TEMPLATE = {
    "form_name": "Management Book Entry",
    "fields": [
        {"key": "entry_date", "label": "日期", "type": "date"},
        {"key": "resident_name", "label": "住客姓名", "type": "text"},
        {"key": "unit_number", "label": "單位號碼", "type": "text"},
        {"key": "contact_phone", "label": "聯絡電話", "type": "text"},
        {"key": "issue_description", "label": "事項描述", "type": "text"},
        {"key": "action_taken", "label": "處理措施", "type": "text"},
        {"key": "staff_name", "label": "負責職員", "type": "text"},
    ],
    "gpt_prompt": """請從這份管理記錄中提取：日期、住客姓名、單位號碼、聯絡電話、事項描述、處理措施、負責職員。
以JSON格式返回，格式為：
{
  "data": { "entry_date": "...", ... },
  "confidence": { "entry_date": 0.95, ... }
}
"""
}

# Template registry
FORM_TEMPLATES = {
    "GCCF_10K": GCCF_10K_TEMPLATE,
    "MGT_BOOK": MGT_BOOK_TEMPLATE,
}

def get_template(form_type: str):
    """Get form template by type"""
    return FORM_TEMPLATES.get(form_type, GCCF_10K_TEMPLATE)

def get_field_labels(form_type: str):
    """Get field labels for display"""
    template = get_template(form_type)
    return {field["key"]: field["label"] for field in template["fields"]}
