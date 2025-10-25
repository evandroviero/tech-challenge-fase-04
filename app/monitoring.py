from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI

def setup_monitoring(app: FastAPI):
    """Configura o 'instrumentator' do Prometheus para a app FastAPI."""
    Instrumentator().instrument(app).expose(app)