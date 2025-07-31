import os
import uuid
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from openpyxl import load_workbook
from models.template_data import TemplateData
from utils.excel_utils import replace_placeholders_in_sheet
from utils.mapping import process_replacements

logger = logging.getLogger(__name__)
router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logger.debug(f"BASE_DIR: {BASE_DIR}")
TEMPLATE_PATH = os.path.join(BASE_DIR, "temp.xlsx")
# TEMPLATE_PATH = r"C:\Users\Acer\Desktop\Nata\Smartwood\apiGetDataToExcel\temp.xlsx"
logger.debug(f"TEMPLATE_PATH: {os.path.abspath(TEMPLATE_PATH)}")

@router.post("/generate-excel/")
async def generate_excel(data: TemplateData):
    try:
        logger.debug(f"Received data: {data.replacements}")
        logger.debug(f"Checking template at: {os.path.abspath(TEMPLATE_PATH)}")
        if not os.path.exists(TEMPLATE_PATH):
            raise HTTPException(status_code=404, detail=f"Template file not found at {os.path.abspath(TEMPLATE_PATH)}")

        wb = load_workbook(TEMPLATE_PATH)
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            replace_placeholders_in_sheet(sheet, data.replacements or {})

        output_filename = f"output_{uuid.uuid4()}.xlsx"
        output_path = os.path.join(BASE_DIR, "temp", output_filename)
        os.makedirs(os.path.join(BASE_DIR, "temp"), exist_ok=True)
        wb.save(output_path)
        
        logger.debug(f"File generated at: {output_path}")
        return FileResponse(
            path=output_path,
            filename=output_filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        logger.error(f"Error generating Excel file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating Excel file: {str(e)}")

@router.post("/generate-excel-2/")
async def generate_excel_2(data: dict):
    try:
        logger.debug(f"Template path: {os.path.abspath(TEMPLATE_PATH)}")
        if not os.path.exists(TEMPLATE_PATH):
            raise HTTPException(status_code=404, detail=f"Template file not found at {os.path.abspath(TEMPLATE_PATH)}")

        wb = load_workbook(TEMPLATE_PATH)
        flat_replacements = process_replacements(data)

        for sheet_name in wb.sheetnames:
            logger.debug(f"Processing sheet: {sheet_name}")
            sheet = wb[sheet_name]
            replace_placeholders_in_sheet(sheet, flat_replacements)

        os.makedirs(os.path.join(BASE_DIR, "temp"), exist_ok=True)
        if not os.access(os.path.join(BASE_DIR, "temp"), os.W_OK):
            raise HTTPException(status_code=500, detail="No write permission for temp folder")

        output_filename = f"output_{uuid.uuid4()}.xlsx"
        output_path = os.path.join(BASE_DIR, "temp", output_filename)
        wb.save(output_path)

        return FileResponse(
            path=output_path,
            filename=output_filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        logger.error(f"Error generating Excel: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating Excel: {str(e)}")