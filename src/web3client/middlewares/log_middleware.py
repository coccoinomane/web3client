from abc import ABC
from typing import Any, Callable, Collection, List, Type

from web3 import Web3
from web3._utils.compat import TypedDict
from web3.types import Middleware, RPCEndpoint, RPCResponse


class BaseLog(ABC):
    """Class meant to be used by the log middleware to log requests and responses"""

    def __init__(
        self,
        method: RPCEndpoint,
        params: Any,
        w3: Web3,
        rpc_whitelist: Collection[str] = None,
    ) -> None:
        self.method = method
        self.params = params
        self.w3 = w3
        self.rpc_whitelist = rpc_whitelist
        self.init()

    def init(self) -> None:
        """Initialization function called in the constructor"""
        pass

    def should_log_request(self) -> bool:
        if self.rpc_whitelist is None:
            return True
        return self.method in self.rpc_whitelist

    def log_request(self) -> None:
        pass

    def should_log_response(self) -> bool:
        if self.rpc_whitelist is None:
            return True
        return self.method in self.rpc_whitelist

    def log_response(self, response: RPCResponse) -> None:
        pass


class InternalLogEntry(TypedDict):
    method: RPCEndpoint
    params: Any
    response: RPCResponse


class Web3WithInternalLog(Web3):
    internal_log: List[InternalLogEntry]


class InternalLog(BaseLog):
    """A log class that keeps track of requests and responses in the
    ``w3.internal_log`` variable"""

    w3: Web3WithInternalLog

    def init(self) -> None:
        if not hasattr(self.w3, "internal_log"):
            self.w3.internal_log = []

    def log_response(self, response: RPCResponse) -> None:
        self.w3.internal_log.append(
            {
                "method": self.method,
                "params": self.params,
                "response": response,
            }
        )

    def get_internal_log(self) -> List[InternalLogEntry]:
        return self.w3.internal_log


def construct_log_middleware(
    log_class: Type[BaseLog], rpc_whitelist: List[str] = None
) -> Middleware:
    """
    Constructs a middleware which logs requests and/or responses based on the
    request ``method`` and ``params``

    :param log: A instance of the ``BaseLog`` class
    """

    def log_middleware(
        make_request: Callable[[RPCEndpoint, Any], RPCResponse], w3: Web3
    ) -> Callable[[RPCEndpoint, Any], RPCResponse]:
        def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
            log = log_class(
                method=method, params=params, w3=w3, rpc_whitelist=rpc_whitelist
            )
            if log.should_log_request():
                log.log_request()
            response = make_request(method, params)
            if log.should_log_response():
                log.log_response(response)
            return response

        return middleware

    return log_middleware


##############################
## Ready to use middlewares
##############################

internal_log_middleware = construct_log_middleware(InternalLog)
