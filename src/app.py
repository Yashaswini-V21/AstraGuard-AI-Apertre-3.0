"""
AstraGuard AI - Main FastAPI Application Entry Point.

This module serves as the primary entry point for production deployments using
Uvicorn. It imports the initialized `app` from `api.service` and configures
the server settings (host, port, workers) for standalone execution.
"""

import os
import sys
import signal
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger: logging.Logger = logging.getLogger(__name__)

try:
    from api.service import app
except ImportError as e:
    logger.critical("Failed to import application – missing dependencies: %s", e, exc_info=True)
    logger.info("Ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    logger.critical("Application initialization failed: %s", e, exc_info=True)
    sys.exit(1)

VALID_LOG_LEVELS: frozenset[str] = frozenset(
    {"critical", "error", "warning", "info", "debug", "trace"}
)

_EADDRINUSE: frozenset[int] = frozenset({48, 98})
_EACCES: int = 13

def _parse_port(value: str) -> int:
    """Parse and validate a port number string.

    Raises:
        SystemExit: if the value is not a valid port number.
    """
    try:
        port = int(value)
    except ValueError:
        logger.error("APP_PORT must be an integer, got: %r", value)
        sys.exit(1)

    if not (1 <= port <= 65535):
        logger.error("APP_PORT must be between 1 and 65535, got: %d", port)
        sys.exit(1)

    return port

def _parse_workers(value: str) -> int:
    """Parse and validate the worker-count string.

    Raises:
        SystemExit: if the value is not a positive integer.
    """
    try:
        workers = int(value)
    except ValueError:
        logger.error("APP_WORKERS must be an integer, got: %r", value)
        sys.exit(1)

    if workers < 1:
        logger.error("APP_WORKERS must be >= 1, got: %d", workers)
        sys.exit(1)

    return workers

def _parse_log_level(value: str) -> str:
    """Normalise and validate a log-level string.

    Falls back to "info" with a warning rather than hard-exiting, so a
    misconfigured LOG_LEVEL never prevents the server from starting.
    """
    normalised = value.strip().lower()
    if normalised not in VALID_LOG_LEVELS:
        logger.warning(
            "Invalid LOG_LEVEL %r – falling back to 'info'. "
            "Valid levels: %s",
            value,
            ", ".join(sorted(VALID_LOG_LEVELS)),
        )
        return "info"
    return normalised

def signal_handler(sig: int, _frame: object) -> None:
    """Handle SIGINT / SIGTERM for a clean shutdown.

    Exposed as a public name so it can be referenced or patched by tests
    and external tooling.  Registered internally via :func:`main`.
    """
    logger.info("Received signal %d – shutting down gracefully.", sig)
    sys.exit(0)

def main() -> None:
    """Configure and start the Uvicorn server."""
    host = os.environ.get("APP_HOST", "0.0.0.0")
    port = _parse_port(os.environ.get("APP_PORT", "8002"))
    workers = _parse_workers(os.environ.get("APP_WORKERS", "1"))
    log_level = _parse_log_level(os.environ.get("LOG_LEVEL", "info"))

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info(
        "Starting AstraGuard AI on %s:%d (workers=%d, log_level=%s)",
        host, port, workers, log_level,
    )

    try:
        import uvicorn
    except ImportError:
        logger.critical("uvicorn is not installed.  Run: pip install uvicorn[standard]")
        sys.exit(1)

    try:
        uvicorn.run(
            "api.service:app" if workers > 1 else app,
            host=host,
            port=port,
            workers=workers if workers > 1 else None,
            log_level=log_level,
            access_log=True,
            server_header=False,
            date_header=True,
        )
    except OSError as e:
        if e.errno in _EADDRINUSE:
            logger.error(
                "Port %d is already in use.  "
                "Set APP_PORT to a different port and retry.",
                port,
            )
        elif e.errno == _EACCES:
            logger.error(
                "Permission denied binding to %s:%d.  "
                "Ports below 1024 require elevated privileges.",
                host, port,
            )
        else:
            logger.error("Failed to start server: %s", e, exc_info=True)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user.")
        sys.exit(0)
    except Exception as e:  # noqa: BLE001
        logger.critical("Unexpected server error: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()