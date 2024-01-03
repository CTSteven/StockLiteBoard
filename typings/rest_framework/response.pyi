from rest_framework.status import HTTP_200_OK
from typing import Any, Dict, Optional

class Response:
    def __init__(self, data: Optional[Dict[str, Any]] = None, status: Optional[int] = HTTP_200_OK): ...