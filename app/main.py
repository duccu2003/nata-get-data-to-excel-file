import os
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middleware import setup_middleware
from routes import invoice, excel, callbacks

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="NATA Data to Excel API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_middleware(app)

# Include routers with explicit prefixes
app.include_router(invoice.router, prefix="/invoice", tags=["invoice"])
app.include_router(excel.router, prefix="/excel", tags=["excel"])
app.include_router(callbacks.router, prefix="/callbacks", tags=["callbacks"])

logger.info("Routers included successfully")
logger.info(f"Callbacks router prefix: /callbacks")

@app.on_event("startup")
async def startup_event():
    """Log available routes on startup"""
    logger.info("FastAPI application starting up...")
    logger.info("Available routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            if hasattr(route, 'methods'):
                logger.info(f"  {route.methods} {route.path}")
            else:
                # WebSocket routes don't have methods
                logger.info(f"  WebSocket {route.path}")

@app.get("/")
async def read_root():
    return {"message": "Welcome to FastAPI!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import asyncio
    # Only use Windows event loop policy on Windows
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    logger.info("Starting FastAPI server with WebSocket support...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")