from typing import Type, Dict

from bottex2.handler import HandlerMiddleware
from bottex2.server import Server


class MiddlewareManager:
    def __init__(self):
        self.middlewares = {}  # type: Dict[Type[HandlerMiddleware], Dict[Type[Server], Type[HandlerMiddleware]]]

    def register_child(self,
                       parent: Type[HandlerMiddleware],
                       server_cls: Type[Server],
                       middleware: Type[HandlerMiddleware]):
        children = self.get_children(parent)
        children[server_cls] = middleware

    def get_children(self, parent: Type[HandlerMiddleware]) -> Dict[Type[Server], Type[HandlerMiddleware]]:
        for registered_parent, children in self.middlewares.items():
            if issubclass(parent, registered_parent):
                return children
        children = {}
        self.middlewares[parent] = children
        return children

    def get_child(self,
                  parent: Type[HandlerMiddleware],
                  server_cls: Type[Server]) -> Type[HandlerMiddleware]:
        child = self.get_children(parent).get(server_cls)
        if child is None:
            return parent
        return type(child.__name__, (child, parent), {})
