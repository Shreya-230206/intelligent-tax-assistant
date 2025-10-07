import pytesseract
from PIL import Image
import io

def parse_form16(file_bytes):
    try:
        img = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(img)
        parsed = {}
        
        for line in text.split('\n'):
            line = line.strip()
            if 'Gross Salary' in line:
                digits = ''.join(filter(str.isdigit, line))
                parsed['gross_salary'] = int(digits) if digits else 0
            if 'TDS' in line:
                digits = ''.join(filter(str.isdigit, line))
                parsed['tds'] = int(digits) if digits else 0
        
        # Default if not found
        parsed.setdefault('gross_salary', 0)
        parsed.setdefault('tds', 0)
        
        return parsed
    except Exception as e:
        raise ValueError(f"Parsing error: {str(e)}")
