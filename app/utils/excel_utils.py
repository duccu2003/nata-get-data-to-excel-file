import re
import logging
from openpyxl import load_workbook

logger = logging.getLogger(__name__)

def replace_placeholders_in_sheet(sheet, replacements):
    placeholder_pattern = re.compile(r'\(\d+\)')
    for row in sheet.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str):
                matches = placeholder_pattern.findall(cell.value)
                if matches:
                    new_value = cell.value
                    for match in matches:
                        placeholder_key = match[1:-1]
                        if placeholder_key in replacements:
                            new_value = new_value.replace(match, str(replacements[placeholder_key]))
                        else:
                            logger.warning(f"No replacement found for placeholder: {match}")
                    cell.value = new_value