# biometric_api/main.py

from fastapi import FastAPI

from biometric_api.logging_config import setup_logging
from biometric_api.routes import health, enroll, scan, employees
from dotenv import load_dotenv
load_dotenv()   # <-- ensures .env is read
# Initialise logging as early as possible
log = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Biometric Clock API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Mount routers
# health:    /health, /api/health
# enroll:    /api/enrol
# scan:      /api/template/{id}, /api/scan
# employees: /api/employees/search
app.include_router(enroll.router, prefix="/api")
app.include_router(scan.router, prefix="/api")
app.include_router(employees.router, prefix="/api")
app.include_router(health.router)


if __name__ == "__main__":
    import uvicorn

    # For local dev; in production you’ll usually run uvicorn via CLI / service
    uvicorn.run(app, host="127.0.0.1", port=7072)
