import re
import logging
from openpyxl import load_workbook
import json
from openpyxl.utils import get_column_letter
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


def update_dpl_sheet(sheet, dpl_data):
    try:
        containers = json.loads(dpl_data)
    except json.JSONDecodeError:
        raise ValueError("Invalid DPL data format")

    total_row = None
    bulk_in_row = None
    cellmark_row = None
    
    for idx, row in enumerate(sheet.iter_rows(min_row=1, max_row=sheet.max_row, values_only=True), 1):
        if row and row[1] and "TOTAL" in str(row[1]):
            total_row = idx
        if row and row[1] and "BULK IN" in str(row[1]):
            bulk_in_row = idx
        if row and row[1] and "Cellmark" in str(row[1]):
            cellmark_row = idx

    if not total_row or not bulk_in_row or not cellmark_row:
        raise ValueError("Could not find summary rows in DPL sheet")

    for row in range(3, total_row):
        sheet[f'B{row}'] = None
        sheet[f'C{row}'] = None
        sheet[f'D{row}'] = None
        sheet[f'E{row}'] = None
        sheet[f'F{row}'] = None

    num_containers = len(containers)
    
    available_rows = total_row - 3
    
    if num_containers > available_rows:
        rows_to_add = num_containers - available_rows
        sheet.insert_rows(3, amount=rows_to_add)
        total_row += rows_to_add
        bulk_in_row += rows_to_add
        cellmark_row += rows_to_add

    for i, container in enumerate(containers):
        row_num = 3 + i
        sheet[f'B{row_num}'] = i + 1
        sheet[f'C{row_num}'] = container.get('contNo', '')
        sheet[f'D{row_num}'] = container.get('sealNo', '')
        sheet[f'E{row_num}'] = container.get('weightNet', 0)
        sheet[f'F{row_num}'] = container.get('weightGross', 0)

    total_net = sum(container.get('weightNet', 0) for container in containers)
    total_gross = sum(container.get('weightGross', 0) for container in containers)

    sheet[f'E{total_row}'] = total_net
    sheet[f'F{total_row}'] = total_gross
    sheet[f'B{bulk_in_row}'] = f"BULK IN : {num_containers} X 20 GP CONTAINERS"