from abc import ABC
from typing import Any, Callable, Collection, List

from web3 import Web3
from web3._utils.compat import TypedDict
from web3.types import Middleware, RPCEndpoint, RPCResponse


class BaseRpcLog(ABC):
    """Class meant to be used by a middleware to log RPC requests and responses"""

    def __init__(self, rpc_whitelist: Collection[str] = None) -> None:
        self.rpc_whitelist = rpc_whitelist
        self.init()

    def init(self) -> None:
        """Initialization function called in the constructor"""
        pass

    def should_log_request(self, method: RPCEndpoint, params: Any, w3: Web3) -> bool:
        if self.rpc_whitelist is None:
            return True
        return method in self.rpc_whitelist

    def log_request(self, method: RPCEndpoint, params: Any, w3: Web3) -> None:
        pass

    def should_log_response(
        self, method: RPCEndpoint, params: Any, w3: Web3, response: RPCResponse
    ) -> bool:
        if self.rpc_whitelist is None:
            return True
        return method in self.rpc_whitelist

    def log_response(
        self, method: RPCEndpoint, params: Any, w3: Web3, response: RPCResponse
    ) -> None:
        pass


class InternalRpcLog(BaseRpcLog):
    """An RPC log class that keeps track of requests and responses in the
    self.entries internal attribute"""

    class Entry(TypedDict):
        method: RPCEndpoint
        params: Any
        response: RPCResponse

    entries: List[Entry]

    def init(self) -> None:
        if not hasattr(self, "internal_log"):
            self.entries = []

    def log_response(
        self, method: RPCEndpoint, params: Any, w3: Web3, response: RPCResponse
    ) -> None:
        self.entries.append({"method": method, "params": params, "response": response})


def construct_rpc_log_middleware(log: BaseRpcLog) -> Middleware:
    """
    Constructs a middleware which logs requests and/or responses based on the
    request ``method`` and ``params``.

    :param rpc_log: A instance of an RPC log class derived from ``BaseRpcLog``.
    """

    def log_middleware(
        make_request: Callable[[RPCEndpoint, Any], RPCResponse], w3: Web3
    ) -> Callable[[RPCEndpoint, Any], RPCResponse]:
        def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
            if log.should_log_request(method, params, w3):
                log.log_request(method, params, w3)
            response = make_request(method, params)
            if log.should_log_response(method, params, w3, response):
                log.log_response(method, params, w3, response)
            return response

        return middleware

    return log_middleware


##############################
## Ready to use middlewares
##############################

internal_log_middleware = construct_rpc_log_middleware(InternalRpcLog())
