"""
Middleware personalizado de trazabilidad para device_systems (Fase 10).

Agrega a cada respuesta:
- X-App-Name: device_systems
- X-Process-Time: tiempo de procesamiento en segundos
- X-Request-ID: identificador unico de la peticion (propagado si el cliente lo envia)

Ademas registra en el log: metodo, ruta, codigo de estado y tiempo de respuesta.
"""
from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("device_systems.requests")
logging.basicConfig(level=logging.INFO)


class RequestTracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time
        response.headers["X-App-Name"] = "device_systems"
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "method=%s path=%s status_code=%s process_time=%.4fs request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
            request_id,
        )
        return response
