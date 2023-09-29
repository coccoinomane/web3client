from abc import ABC
from datetime import datetime
from typing import Any, Callable, Collection, List

from typing_extensions import Literal, NotRequired
from web3 import Web3
from web3._utils.compat import TypedDict
from web3.types import Middleware, RPCEndpoint, RPCResponse, TxData

from web3client.helpers.tx import parse_raw_tx


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


class MemoryLog(BaseRpcLog):
    """An RPC log class that keeps track of requests and responses in the
    self.entries internal attribute"""

    class Entry(TypedDict):
        type: Literal["request", "response"]
        timestamp: datetime
        method: str
        params: Any
        response: NotRequired[RPCResponse]

    entries: List[Entry]

    def init(self) -> None:
        self.entries = []

    def log_request(self, method: RPCEndpoint, params: Any, w3: Web3) -> None:
        self.entries.append(
            {
                "type": "request",
                "timestamp": datetime.now(),
                "method": method,
                "params": params,
            }
        )

    def log_response(
        self, method: RPCEndpoint, params: Any, w3: Web3, response: RPCResponse
    ) -> None:
        self.entries.append(
            {
                "type": "response",
                "timestamp": datetime.now(),
                "method": method,
                "params": params,
                "response": response,
            }
        )


class TxMemoryLog(MemoryLog):
    """Decode and track transaction-related requests.  Ignore the
    responses.

    It tracks and decodes requests to the following RPC methods:
     - eth_sendRawTransaction
     - eth_call
     - eth_estimateGas

    Whenever a request to one of these methods is made, the request is decoded
    into a TxData object, which is then stored in the ``tx_entries`` attribute.

    Make sure to include the methods you want to track in the ``rpc_whitelist``
    parameter."""

    tx_entries: List[TxData]

    def init(self) -> None:
        super().init()
        self.tx_entries = []

    def log_request(self, method: RPCEndpoint, params: Any, w3: Web3) -> None:
        super().log_request(method, params, w3)
        if method == "eth_sendRawTransaction":
            self.tx_entries.append(parse_raw_tx(params[0]))
        # elif method == "eth_call":
        #     self.tx_entries.append(parse_raw_tx(params[0]["data"]))
        # elif method == "eth_estimateGas":
        #     self.tx_entries.append(parse_raw_tx(params[0]["data"]))


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
