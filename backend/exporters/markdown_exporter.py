from typing import Dict, Any, List
from ocr.templates import get_template, get_field_labels

def export_to_markdown(data: Dict[str, Any], form_type: str, confidence: Dict[str, float] = None) -> str:
    """
    Export OCR results to formatted Markdown
    """
    template = get_template(form_type)
    field_labels = get_field_labels(form_type)
    
    md_lines = []
    
    # Title
    md_lines.append(f"# {template['form_name']}")
    md_lines.append("")
    
    # Group fields by section (based on typical form structure)
    sections = _group_fields_by_section(template["fields"])
    
    for section_name, fields in sections.items():
        md_lines.append(f"## {section_name}")
        md_lines.append("")
        md_lines.append("| 字段 | 內容 | 置信度 |")
        md_lines.append("|------|------|--------|")
        
        for field in fields:
            key = field["key"]
            label = field["label"]
            value = data.get(key, "N/A")
            conf = confidence.get(key, 0.0) if confidence else 0.0
            conf_str = f"{conf:.2%}" if conf > 0 else "N/A"
            
            # Format value
            if value is None:
                value = "N/A"
            
            md_lines.append(f"| {label} | {value} | {conf_str} |")
        
        md_lines.append("")
    
    return "\n".join(md_lines)

def _group_fields_by_section(fields: List[Dict]) -> Dict[str, List[Dict]]:
    """Group fields into logical sections based on keywords"""
    sections = {
        "申請人基本資料": [],
        "就業資料": [],
        "家庭資料": [],
        "財務資料": [],
        "申請資料": [],
        "其他資料": []
    }
    
    for field in fields:
        key = field["key"]
        label = field["label"]
        
        if any(kw in label for kw in ["申請人", "姓名", "身份證", "出生", "電話", "住址", "聯絡"]):
            sections["申請人基本資料"].append(field)
        elif any(kw in key or kw in label for kw in ["employ", "occupation", "income", "salary", "就業", "職業", "收入"]):
            sections["就業資料"].append(field)
        elif any(kw in key or kw in label for kw in ["family", "member", "marital", "家庭", "婚姻"]):
            sections["家庭資料"].append(field)
        elif any(kw in key or kw in label for kw in ["rent", "asset", "debt", "financial", "租金", "資產", "負債"]):
            sections["財務資料"].append(field)
        elif any(kw in key or kw in label for kw in ["application", "amount", "purpose", "date", "申請", "金額", "目的", "日期"]):
            sections["申請資料"].append(field)
        else:
            sections["其他資料"].append(field)
    
    # Remove empty sections
    return {k: v for k, v in sections.items() if v}
