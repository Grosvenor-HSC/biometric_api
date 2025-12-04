# biometric_api/main.py

from fastapi import FastAPI

from biometric_api.logging_config import setup_logging
from biometric_api.routes import health, enroll, scan, employees, template  # <-- add template
from dotenv import load_dotenv

load_dotenv()
log = setup_logging()

app = FastAPI(
    title="Biometric Clock API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# health:    /health, /api/health
# enroll:    /api/enrol
# scan:      /api/scan
# employees: /api/employees/search
# template:  /api/template/{id}
app.include_router(enroll.router, prefix="/api")
app.include_router(scan.router, prefix="/api")
app.include_router(employees.router, prefix="/api")
app.include_router(template.router, prefix="/api")  # <-- mount template router
app.include_router(health.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=7072)
