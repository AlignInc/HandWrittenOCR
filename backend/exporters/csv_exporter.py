import csv
import io
from typing import List, Dict, Any
from ocr.templates import get_template, get_field_labels

def export_to_csv(batches_data: List[Dict[str, Any]], form_type: str) -> str:
    """
    Export batch results to CSV format
    Each row represents one form/batch
    """
    template = get_template(form_type)
    field_labels = get_field_labels(form_type)
    
    # Prepare CSV headers
    headers = [field["key"] for field in template["fields"]]
    header_labels = [field["label"] for field in template["fields"]]
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    
    # Write header with Chinese labels
    writer.writerow(dict(zip(headers, header_labels)))
    
    # Write data rows
    for batch_data in batches_data:
        row = {}
        for field_key in headers:
            row[field_key] = batch_data.get(field_key, "")
        writer.writerow(row)
    
    return output.getvalue()

def export_single_to_csv(data: Dict[str, Any], form_type: str) -> str:
    """Export single batch to CSV"""
    return export_to_csv([data], form_type)
