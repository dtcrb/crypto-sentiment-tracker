import azure.functions as func
from backend.main import app as fastapi_app  # adjust import to your path

app = func.AsgiFunctionApp(
    app=fastapi_app,
    http_auth_level=func.AuthLevel.ANONYMOUS
)

