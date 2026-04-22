import logging

from pydantic import BaseModel

class LoggingConfig(BaseModel):
        level: int = logging.WARNING
        datefmt: str = "%Y-%m-%d %H:%M:%S"
        format: str = "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
