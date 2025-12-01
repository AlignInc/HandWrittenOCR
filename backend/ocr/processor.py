import cv2
import numpy as np
from PIL import Image
import base64
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import os
from paddleocr import PPStructure, draw_structure_result, save_structure_res
from paddleocr.ppstructure.recovery.recovery_to_doc import sorted_layout_boxes, convert_info_docx
from .templates import FORM_TEMPLATES, get_template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRProcessor:
    
    def __init__(self):
        self.pp_structure = None
        # Initialize PP-StructureV2 for Layout Analysis and Table Recognition
        # table=True enables table recognition
        # ocr=True enables text recognition within blocks
        # Disable image_orientation to avoid requiring extra PULC model download
        self._init_pp_structure()
        
        # Initialize OpenAI client if enabled
        self.use_gpt_vision = os.getenv("USE_GPT_VISION", "false").lower() == "true"
        if self.use_gpt_vision:
            from openai import OpenAI
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            self.client = None

    def _init_pp_structure(self):
        """Load PP-Structure models and fail fast with a readable message."""
        try:
            self.pp_structure = PPStructure(
                show_log=True,
                image_orientation=False,
                table=True,
                ocr=True,
                layout=True,
                recovery=True,
                lang='ch',
                use_gpu=False
            )
            logger.info("PP-Structure initialized (lang=ch, gpu=%s)", False)
        except Exception as exc:
            logger.exception("Failed to initialize PP-Structure OCR models.")
            # Raise a descriptive error so the batch processor can surface it
            raise RuntimeError("PP-Structure initialization failed. Check PaddleOCR installation and model files.") from exc

    def preprocess_image(self, image_path):
        """
        Preprocess image for better OCR results
        """
        img = cv2.imread(image_path)
        
        # 1. Denoising
        dst = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        
        # 2. Convert to grayscale
        gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
        
        # 3. Contrast enhancement (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # 4. Binarization (Otsu's method) - Optional, sometimes grayscale is better for CNNs
        # _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return img, gray

    def extract_text_paddle(self, image_path):
        """
        Use PP-StructureV2 to extract text and structure
        """
        try:
            if not self.pp_structure:
                raise RuntimeError("PP-Structure is not initialized.")

            if not Path(image_path).exists():
                raise FileNotFoundError(f"Image not found: {image_path}")

            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Failed to read image from path: {image_path}")
            
            # Run layout analysis
            result = self.pp_structure(img)
            
            # Extract text from results
            # PPStructure returns a list of dicts, each containing 'type', 'bbox', 'res'
            # 'res' contains 'text_region', 'text', 'confidence' etc.
            
            full_text = []
            structured_data = []
            
            for region in result or []:
                region_type = region.get('type', '')
                res = region.get('res', [])
                
                # Handle Table regions
                if region_type == 'table':
                    # Table html is in res['html'] – extract plain text as fallback
                    if isinstance(res, dict):
                        html = res.get('html') or ''
                        if html:
                            import re
                            plain = re.sub('<[^<]+?>', ' ', html)
                            plain = ' '.join(plain.split())
                            if plain:
                                full_text.append(plain)
                        # some versions store cell texts under 'cell'
                        cells = res.get('cell') or res.get('cells') or []
                        if isinstance(cells, list):
                            for c in cells:
                                txt = c.get('text') if isinstance(c, dict) else None
                                if txt:
                                    full_text.append(txt)
                    # keep placeholder to signal table presence
                    full_text.append("[TABLE DATA]")
                
                # Handle Text/Title/Header regions
                elif region_type in ['text', 'title', 'header', 'footer']:
                    # For text regions, res is a list of dicts with 'text' field
                    # Note: PPStructure structure might vary slightly by version, 
                    # but typically for 'text' type, 'res' is a list of line results
                    if isinstance(res, list):
                        for line in res:
                            if isinstance(line, dict) and 'text' in line:
                                text = line['text']
                                confidence = line.get('confidence', 0.0)
                                full_text.append(text)
                                structured_data.append({
                                    "text": text,
                                    "confidence": confidence,
                                    "bbox": region.get('bbox'),
                                    "type": region_type
                                })
            
            raw_text = "\n".join(full_text)

            if not raw_text.strip():
                raise ValueError("OCR engine returned empty text.")
            
            # Calculate average confidence
            confidences = [item['confidence'] for item in structured_data if 'confidence' in item]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return raw_text, avg_confidence, structured_data
            
        except Exception as e:
            logger.exception("PaddleOCR processing failed for %s", image_path)
            # Bubble up so caller can mark the batch as failed
            raise

    def extract_structured_data(self, raw_text: str, form_type="GCCF_10K_P1", ocr_results=None):
        """
        Extract structured fields based on form template
        """
        template = FORM_TEMPLATES.get(form_type, FORM_TEMPLATES["GCCF_10K_P1"])
        extracted_data = {}
        field_confidences = {}
        
        # Simple rule-based extraction (fallback)
        # In a real scenario, we would use the bounding boxes from ocr_results 
        # to map text to fields based on spatial layout
        
        lines = raw_text.split('\n')
        
        for field in template["fields"]:
            key = field["key"]
            label = field["label"]
            
            # Try to find the label in the text and get the value after it
            value = None
            confidence = 0.0
            
            # 1. Direct line matching
            for i, line in enumerate(lines):
                if label in line:
                    # Value might be on the same line
                    parts = line.split(label)
                    if len(parts) > 1 and parts[1].strip():
                        value = parts[1].strip().replace(":", "").replace("：", "").strip()
                        confidence = 0.8
                    # Or on the next line
                    elif i + 1 < len(lines):
                        value = lines[i+1].strip()
                        confidence = 0.7
                    break
            
            extracted_data[key] = value
            field_confidences[key] = confidence

        return extracted_data, field_confidences

    def detect_form_type(self, raw_text: str, image_path: str = "") -> str:
        """
        Heuristic form-type detection based on text cues and filename.
        """
        text_lower = (raw_text or "").lower()
        fname = Path(image_path).name.lower() if image_path else ""

        # Filename hints
        if "a01" in fname or "roster" in fname or "owner" in fname or "mgt" in fname:
            return "HOUSE_ROSTER"
        if "p2" in fname:
            return "GCCF_10K_P2"
        if "p1" in fname:
            return "GCCF_10K_P1"

        # Content hints
        if "調查人員" in raw_text or "聲明及承諾" in raw_text or "undertaking" in text_lower:
            return "GCCF_10K_P2"
        if "申請人家屬" in raw_text or "現職" in raw_text or "華人慈善基金" in raw_text:
            return "GCCF_10K_P1"
        if ("單位" in raw_text and "業主姓名" in raw_text) or "owner name" in text_lower:
            return "HOUSE_ROSTER"

        return "GCCF_10K_P1"

    def extract_with_gpt_vision(self, image_path, form_type="GCCF_10K_P1"):
        """
        Use GPT-4 Vision for intelligent extraction
        """
        if not self.use_gpt_vision or not self.client:
            return None, None

        import base64
        
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        base64_image = encode_image(image_path)
        template = FORM_TEMPLATES.get(form_type, FORM_TEMPLATES["GCCF_10K_P1"])
        
        prompt = template.get("gpt_prompt", "Extract all fields from this form.")

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            # Parse JSON from response
            # This assumes GPT returns valid JSON wrapped in markdown code blocks or raw
            try:
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0]
                else:
                    json_str = content
                
                data = json.loads(json_str)
                return data, {k: 0.95 for k in data.keys()} # High confidence for GPT
                
            except json.JSONDecodeError:
                logger.error(f"GPT-4 Vision response was not valid JSON: {content}")
                return None, None
            except Exception as e:
                logger.error(f"Error parsing GPT-4 Vision response: {e}")
                return None, None
        except Exception as e:
            logger.exception("GPT-4 Vision API call failed for %s", image_path)
            return None, None

    # Assuming there's a process_document method that uses the above
    # Adding a placeholder for context based on the user's edit
    def process_document(self, image_path, form_type="AUTO"):
        """
        End-to-end document processing that returns a unified result dict
        expected by downstream callers:
        {
          "data": {...},
          "confidence": {...},
          "raw_text": "...",
          "method": "paddle_ocr" | "gpt-4-vision",
          "form_type": "detected template name"
        }
        """

        result = {"data": {}, "confidence": {}, "raw_text": "", "method": "paddle_ocr", "form_type": form_type}
        
        # Preprocess image (optional, depending on PaddleOCR's internal preprocessing)
        # img, gray_img = self.preprocess_image(image_path)
        
        # Extract text and structure using PaddleOCR
        raw_text, avg_confidence, paddle_results = self.extract_text_paddle(image_path)
        result["raw_text"] = raw_text

        # Auto-detect form if required
        detected_type = form_type
        if form_type in (None, "", "AUTO"):
            detected_type = self.detect_form_type(raw_text, image_path)
            result["form_type"] = detected_type
        else:
            result["form_type"] = form_type
        
        # Try GPT-4 Vision if enabled
        if self.use_gpt_vision and self.client:
            try:
                gpt_data, gpt_confidence = self.extract_with_gpt_vision(image_path, detected_type)
                if gpt_data:
                    result["data"] = gpt_data
                    result["confidence"] = gpt_confidence
                    result["method"] = "gpt-4-vision"
                    return result
            except Exception as e:
                logger.error(f"GPT-4 Vision failed, falling back to template matching: {e}")

        # Fallback: Use template-based extraction from PaddleOCR results
        layout_data, layout_conf = self._template_based_extraction(
            raw_text, paddle_results, detected_type
        )
        rule_data, rule_conf = self.extract_structured_data(raw_text, detected_type, paddle_results)

        # Merge heuristic extraction so we return whatever signal we have
        merged_data = {}
        merged_conf = {}
        template = get_template(detected_type)
        for field in template["fields"]:
            key = field["key"]
            layout_val = layout_data.get(key)
            rule_val = rule_data.get(key)

            if layout_val not in (None, ""):
                merged_data[key] = layout_val
                merged_conf[key] = layout_conf.get(key, 0.0)
            elif rule_val not in (None, ""):
                merged_data[key] = rule_val
                merged_conf[key] = rule_conf.get(key, 0.0)
            else:
                merged_data[key] = None
                merged_conf[key] = 0.0

        result["data"] = merged_data
        result["confidence"] = merged_conf

        # If nothing meaningful extracted, at least return full raw text
        if not any(v for v in result["data"].values() if v not in (None, "")):
            result["data"] = {"full_text": raw_text}
            # use average confidence if available, else 0
            try:
                confidences = [c for c in result["confidence"].values() if isinstance(c, (int, float))]
                avg = sum(confidences) / len(confidences) if confidences else 0.0
            except Exception:
                avg = 0.0
            result["confidence"] = {"full_text": avg}
        
        return result
    
    def _template_based_extraction(
        self, 
        raw_text: str, 
        paddle_results: list, 
        form_type: str
    ) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """
        Extract fields using template matching on PaddleOCR results
        This is a simple keyword-based approach - can be enhanced with regex/NLP
        """
        template = get_template(form_type)
        data = {}
        confidence = {}
        
        # Simple keyword matching for demonstration
        # In production, you'd use more sophisticated NLP or regex patterns
        text_lower = raw_text.lower()
        
        for field in template["fields"]:
            key = field["key"]
            label = field["label"]
            
            # Try to find label in text and extract value after it
            # This is very basic - enhance based on your specific forms
            for line in paddle_results:
                line_text = line["text"]
                if label in line_text or any(keyword in line_text for keyword in [key, label.replace("申請人", "")]):
                    # Extract the value (simplified logic)
                    data[key] = line_text
                    confidence[key] = line["confidence"]
                    break
            
            # Set defaults for missing fields
            if key not in data:
                data[key] = None
                confidence[key] = 0.0
        
        return data, confidence

# Global processor instance
_processor = None

def get_processor() -> OCRProcessor:
    """Get or create OCR processor singleton"""
    global _processor
    if _processor is None:
        _processor = OCRProcessor()
    return _processor
