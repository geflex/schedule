from typing import Callable, Optional

from bottex.messaging import Request
from bottex.messaging.responses import Message


Receiver = Callable[[Request], Optional[Message]]
ErrorHandler = Callable[[Request, Exception], Message]
Match = Callable[[Request], bool]
