from typing import Optional

from bottex2.handler import Handler
from bottex2.router import Router, TCondition


class DecoratorRouter:
    def __init__(self, router: Router):
        self._router = router

    def set_default(self, handler: Handler) -> Handler:
        self._router.default_handler = handler
        return handler

    def register(self, *conditions: Optional[TCondition]):
        """Decorator to register handler for described conditions"""
        for condition in conditions:
            router = self._router.routes[condition]
        return self.set_default
