import os
import logging
import uvicorn
from fastapi import FastAPI
from middleware import setup_middleware
from routes import invoice, excel

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

setup_middleware(app)

app.include_router(invoice.router, prefix="/invoice")
app.include_router(excel.router, prefix="/excel")

@app.get("/")
async def read_root():
    return {"message": "Welcome to FastAPI!"}

if __name__ == "__main__":
    import asyncio
    # Only use Windows event loop policy on Windows
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run(app, host="0.0.0.0", port=8000)