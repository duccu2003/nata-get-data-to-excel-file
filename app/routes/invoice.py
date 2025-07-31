from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
# from demo import fill_invoice_template, get_invoice_data

router = APIRouter()

# @router.get("/get_invoice_data/")
# async def get_data(contract_number: str):
#     result = get_invoice_data(contract_number)
#     if not result:
#         raise HTTPException(status_code=404, detail="Contract not found")
#     return result

# @router.get("/export-invoice/")
# async def export_invoice(contract_number: str):
#     template = "Copy of Custom_Doc-DOCUMENTS_5855_TEMPLATE.xlsx"
#     output = f"invoice_{contract_number.replace('/', '_')}.xlsx"
    
#     try:
#         path = fill_invoice_template(contract_number, template, output)
#         return FileResponse(path, filename=output)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))