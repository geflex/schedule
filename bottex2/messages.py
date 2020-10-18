from typing import Optional, List


class Message:
    def __init__(self, text: str, raw: Optional[dict] = None):
        self.text = text
        self.raw = {} if raw is None else raw
        self.media = []  # type: List[Message]


class Media:
    def __init__(self, url: str):
        self.url = url
