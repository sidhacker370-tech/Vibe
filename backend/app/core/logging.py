import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Configure standard Python logging
# For production, consider using structlog or similar JSON logger
FORMAT = "%(levelname)s:     %(asctime)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger("app")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process the request
        try:
            response = await call_next(request)
            
            process_time = (time.time() - start_time) * 1000
            formatted_process_time = '{0:.2f}'.format(process_time)
            
            # Log structured info
            logger.info(
                f"method={request.method} path={request.url.path} "
                f"status={response.status_code} "
                f"duration_ms={formatted_process_time}"
            )
            return response
            
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            formatted_process_time = '{0:.2f}'.format(process_time)
            
            logger.error(
                f"method={request.method} path={request.url.path} "
                f"status=500 duration_ms={formatted_process_time} error=\"{str(e)}\"",
                exc_info=True
            )
            raise e
