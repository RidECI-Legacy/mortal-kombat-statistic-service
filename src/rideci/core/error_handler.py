from fastapi import Request, status
from fastapi.responses import JSONResponse
from src.rideci.core.logging import logger

async def global_exception_handler(request: Request, exc: Exception):
    """Captura cualquier excepción no manejada y retorna un error 500 estandarizado."""
    logger.error(f"Unhandled error: {str(exc)} on path {request.url.path}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal Server Error",
            "detail": str(exc) if hasattr(exc, 'message') else "An unexpected error occurred."
        }
    )
